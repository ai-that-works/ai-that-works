import { existsSync, mkdirSync, writeFileSync, appendFileSync } from "node:fs";
import { query, type SDKMessage } from "./agent-sdk";
import { z } from "zod";
import { BLUE, CYAN, GREEN, YELLOW, RESET, log, printEvent } from "./utils";
import { orderStore } from "./store/order-store";
import { driverStore } from "./store/driver-store";
import type { OrderStatus } from "./models/types";

// ============================================================================
// Tracking Log - Persisted State
// ============================================================================

interface NotificationLog {
  orderId: string;
  timestamp: string;
  type: "status_change" | "customer_sms" | "driver_notification";
  message: string;
  metadata?: Record<string, any>;
}

interface TrackingLog {
  workflowId: string;
  status: "in_progress" | "completed" | "error";
  startedAt: string;
  completedAt?: string;
  ordersProcessed: number;
  statusUpdates: number;
  notifications: NotificationLog[];
  error?: { message: string };
}

const LOGS_DIR = "logs";
const SESSION_TS = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const TRACKING_LOG_PATH = `${LOGS_DIR}/delivery-tracking-${SESSION_TS}.json`;
const EVENTS_LOG_PATH = `${LOGS_DIR}/tracking-events-${SESSION_TS}.jsonl`;
const NOTIFICATIONS_LOG_PATH = `${LOGS_DIR}/notifications-${SESSION_TS}.jsonl`;

if (!existsSync(LOGS_DIR)) mkdirSync(LOGS_DIR, { recursive: true });

function saveTrackingLog(trackingLog: TrackingLog) {
  writeFileSync(TRACKING_LOG_PATH, JSON.stringify(trackingLog, null, 2));
  log(`${BLUE}[Saved]${RESET} ${TRACKING_LOG_PATH}`);
}

function logEvent(event: SDKMessage) {
  appendFileSync(EVENTS_LOG_PATH, JSON.stringify(event) + "\n");
}

function logNotification(notification: NotificationLog) {
  appendFileSync(NOTIFICATIONS_LOG_PATH, JSON.stringify(notification) + "\n");
  log(
    `${YELLOW}📱 [Notification]${RESET} ${notification.type}: ${notification.message}`,
  );
}

// ============================================================================
// Delivery Tracking Schema
// ============================================================================

const StatusProgressionSchema = z.object({
  orderId: z.string().describe("The order ID to update"),
  currentStatus: z
    .enum([
      "pending",
      "confirmed",
      "preparing",
      "ready",
      "out_for_delivery",
      "delivered",
      "cancelled",
    ])
    .describe("Current order status"),
  nextStatus: z
    .enum([
      "pending",
      "confirmed",
      "preparing",
      "ready",
      "out_for_delivery",
      "delivered",
      "cancelled",
    ])
    .describe("Next status in the delivery progression"),
  reasoning: z
    .string()
    .describe("Explanation of why this progression is appropriate"),
  estimatedTimeToNext: z
    .number()
    .describe("Estimated time in minutes to next status"),
});

const TrackingOutputSchema = z.object({
  totalActiveOrders: z
    .number()
    .describe("Total number of orders in active delivery states"),
  progressions: z
    .array(StatusProgressionSchema)
    .describe("List of status progressions to apply"),
  notifications: z
    .array(
      z.object({
        orderId: z.string(),
        type: z.enum(["status_change", "customer_sms", "driver_notification"]),
        message: z.string(),
      }),
    )
    .describe("Notifications to send"),
  summary: z.string().describe("Summary of the tracking workflow results"),
});

type TrackingOutput = z.infer<typeof TrackingOutputSchema>;

// ============================================================================
// Status Progression Logic
// ============================================================================

function executeProgressions(output: TrackingOutput): TrackingLog {
  const trackingLog: TrackingLog = {
    workflowId: SESSION_TS,
    status: "in_progress",
    startedAt: new Date().toISOString(),
    ordersProcessed: 0,
    statusUpdates: 0,
    notifications: [],
  };

  log(`\n${CYAN}=== Executing Status Progressions ===${RESET}\n`);

  for (const progression of output.progressions) {
    try {
      // Verify order exists
      const order = orderStore.read(progression.orderId);
      if (!order) {
        log(
          `${YELLOW}[Warning]${RESET} Order ${progression.orderId} not found, skipping`,
        );
        continue;
      }

      // Verify current status matches
      if (order.status !== progression.currentStatus) {
        log(
          `${YELLOW}[Warning]${RESET} Order ${progression.orderId} status mismatch (expected: ${progression.currentStatus}, actual: ${order.status}), skipping`,
        );
        continue;
      }

      // Update order status
      orderStore.update(progression.orderId, {
        status: progression.nextStatus,
      });

      log(
        `${GREEN}✓${RESET} Updated order ${progression.orderId}: ${progression.currentStatus} → ${progression.nextStatus}`,
      );
      log(`  ${CYAN}Reasoning:${RESET} ${progression.reasoning}`);
      log(
        `  ${CYAN}Estimated time:${RESET} ${progression.estimatedTimeToNext} minutes`,
      );

      // If order is delivered, mark driver as available again
      if (progression.nextStatus === "delivered" && order.assignedDriverId) {
        try {
          const driver = driverStore.read(order.assignedDriverId);
          if (driver && driver.status === "busy") {
            driverStore.update(order.assignedDriverId, { status: "available" });
            log(
              `${GREEN}✓${RESET} Driver ${driver.name} (${order.assignedDriverId}) is now available`,
            );
          }
        } catch (error) {
          log(
            `${YELLOW}[Warning]${RESET} Could not update driver status: ${(error as Error).message}`,
          );
        }
      }

      trackingLog.statusUpdates++;
    } catch (error) {
      log(
        `${YELLOW}[Error]${RESET} Failed to update order ${progression.orderId}: ${(error as Error).message}`,
      );
    }
    trackingLog.ordersProcessed++;
  }

  // Process notifications
  log(`\n${CYAN}=== Sending Notifications ===${RESET}\n`);

  for (const notification of output.notifications) {
    const timestamp = new Date().toISOString();
    const notificationLog: NotificationLog = {
      orderId: notification.orderId,
      timestamp,
      type: notification.type,
      message: notification.message,
    };

    logNotification(notificationLog);
    trackingLog.notifications.push(notificationLog);
  }

  trackingLog.status = "completed";
  trackingLog.completedAt = new Date().toISOString();

  return trackingLog;
}

// ============================================================================
// Main Tracking Workflow
// ============================================================================

async function runTrackingWorkflow(): Promise<TrackingOutput> {
  log(`\n${CYAN}=== Delivery Tracking Workflow ===${RESET}\n`);

  // Get orders in active delivery states
  const activeStatuses: OrderStatus[] = [
    "confirmed",
    "preparing",
    "ready",
    "out_for_delivery",
  ];

  const activeOrders = activeStatuses.flatMap((status) =>
    orderStore.list({ status }),
  );

  log(`${BLUE}[Info]${RESET} Found ${activeOrders.length} orders in active delivery states`);

  if (activeOrders.length === 0) {
    log(`${YELLOW}[Info]${RESET} No active orders to track`);
    return {
      totalActiveOrders: 0,
      progressions: [],
      notifications: [],
      summary:
        "No active orders found. Workflow completed with no status updates.",
    };
  }

  // Prepare context for the AI
  const ordersContext = activeOrders
    .map((o) => {
      const driverInfo = o.assignedDriverId
        ? ` (Driver: ${o.assignedDriverId})`
        : " (No driver assigned)";
      return `- Order ${o.id}: Status '${o.status}', Customer ${o.customerSnapshot.name}, ${o.items.length} items, $${o.totalAmount.toFixed(2)}${driverInfo}`;
    })
    .join("\n");

  const { $schema: _, ...schema } = z.toJSONSchema(TrackingOutputSchema);

  const prompt = `You are a delivery tracking system for BurritoOps, a burrito delivery service.

Your task is to track active orders and progress them through the delivery lifecycle.

ACTIVE ORDERS:
${ordersContext}

DELIVERY STATUS FLOW:
confirmed → preparing → ready → out_for_delivery → delivered

PROGRESSION RULES:
1. Orders typically spend 10-15 minutes in "confirmed" before moving to "preparing"
2. "preparing" usually takes 15-20 minutes (cooking time)
3. "ready" is a short state (2-5 minutes) before driver picks up
4. "out_for_delivery" typically takes 10-30 minutes depending on distance
5. Simulate realistic progression - not all orders advance at the same rate
6. Some orders may stay in their current state if timing isn't right yet

NOTIFICATION RULES:
1. Send "status_change" notification for each status update
2. Send "customer_sms" when order is out_for_delivery or delivered
3. Send "driver_notification" when order becomes ready (driver should pick up)

Analyze each order's current status and determine appropriate progressions. Be realistic about timing and don't advance all orders simultaneously. Include reasoning for each decision.`;

  const conversation = query({
    prompt,
    options: {
      outputFormat: { type: "json_schema", schema },
    },
  });

  let output: TrackingOutput | undefined;

  for await (const msg of conversation) {
    logEvent(msg);
    printEvent(msg);

    if (msg.type === "result" && msg.subtype === "success") {
      output = (msg as any).structured_output;
    }
  }

  if (!output) {
    throw new Error("Tracking workflow failed to produce output");
  }

  return output;
}

// ============================================================================
// Main Entry Point
// ============================================================================

async function main() {
  log(`${BLUE}╔════════════════════════════════════════╗${RESET}`);
  log(`${BLUE}║   🌯 BurritoOps Delivery Tracking 🚚  ║${RESET}`);
  log(`${BLUE}╚════════════════════════════════════════╝${RESET}`);
  log(`${CYAN}[System]${RESET} Tracking log: ${TRACKING_LOG_PATH}`);
  log(`${CYAN}[System]${RESET} Events log: ${EVENTS_LOG_PATH}`);
  log(`${CYAN}[System]${RESET} Notifications log: ${NOTIFICATIONS_LOG_PATH}\n`);

  let trackingLog: TrackingLog = {
    workflowId: SESSION_TS,
    status: "in_progress",
    startedAt: new Date().toISOString(),
    ordersProcessed: 0,
    statusUpdates: 0,
    notifications: [],
  };

  try {
    // Run the AI-powered tracking workflow
    const output = await runTrackingWorkflow();

    // Execute the progressions
    trackingLog = executeProgressions(output);

    // Save final log
    saveTrackingLog(trackingLog);

    // Print summary
    log(`\n${CYAN}=== Workflow Summary ===${RESET}`);
    log(output.summary);
    log(
      `\n${GREEN}✓${RESET} Workflow completed: ${trackingLog.statusUpdates} status updates made`,
    );
    log(
      `${GREEN}✓${RESET} ${trackingLog.notifications.length} notifications sent`,
    );
    log(`${BLUE}[Info]${RESET} Logs saved to ${TRACKING_LOG_PATH}`);
  } catch (error) {
    trackingLog.status = "error";
    trackingLog.error = { message: (error as Error).message };
    trackingLog.completedAt = new Date().toISOString();
    saveTrackingLog(trackingLog);

    log(`\n${YELLOW}[Error]${RESET} Workflow failed: ${(error as Error).message}`);
    throw error;
  }
}

main();
