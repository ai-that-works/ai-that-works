import { existsSync, mkdirSync, writeFileSync, appendFileSync } from "node:fs";
import { query, type SDKMessage } from "./agent-sdk";
import { z } from "zod";
import { BLUE, CYAN, GREEN, YELLOW, RESET, log, printEvent } from "./utils";
import { orderStore } from "./store/order-store";
import { driverStore } from "./store/driver-store";

// ============================================================================
// Workflow Log - Persisted State
// ============================================================================

interface AssignmentLog {
  workflowId: string;
  status: "in_progress" | "completed" | "error";
  startedAt: string;
  completedAt?: string;
  ordersProcessed: number;
  assignmentsMade: number;
  assignments: Array<{
    orderId: string;
    driverId: string;
    timestamp: string;
  }>;
  error?: { message: string };
}

const LOGS_DIR = "logs";
const SESSION_TS = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const WORKFLOW_LOG_PATH = `${LOGS_DIR}/assignment-workflow-${SESSION_TS}.json`;
const EVENTS_LOG_PATH = `${LOGS_DIR}/assignment-events-${SESSION_TS}.jsonl`;

if (!existsSync(LOGS_DIR)) mkdirSync(LOGS_DIR, { recursive: true });

function saveWorkflowLog(workflowLog: AssignmentLog) {
  writeFileSync(WORKFLOW_LOG_PATH, JSON.stringify(workflowLog, null, 2));
  log(`${BLUE}[Saved]${RESET} ${WORKFLOW_LOG_PATH}`);
}

function logEvent(event: SDKMessage) {
  appendFileSync(EVENTS_LOG_PATH, JSON.stringify(event) + "\n");
}

// ============================================================================
// Assignment Workflow Schema
// ============================================================================

const AssignmentActionSchema = z.object({
  orderId: z.string().describe("The order ID to assign"),
  driverId: z.string().describe("The driver ID to assign to"),
  reasoning: z.string().describe("Explanation of why this driver was chosen"),
});

const WorkflowOutputSchema = z.object({
  totalOrders: z.number().describe("Total number of pending orders found"),
  totalDrivers: z.number().describe("Total number of available drivers found"),
  assignments: z
    .array(AssignmentActionSchema)
    .describe("List of order-to-driver assignments"),
  summary: z.string().describe("Summary of the assignment workflow results"),
});

type WorkflowOutput = z.infer<typeof WorkflowOutputSchema>;

// ============================================================================
// Assignment Logic
// ============================================================================

function executeAssignments(assignments: WorkflowOutput): AssignmentLog {
  const workflowLog: AssignmentLog = {
    workflowId: SESSION_TS,
    status: "in_progress",
    startedAt: new Date().toISOString(),
    ordersProcessed: 0,
    assignmentsMade: 0,
    assignments: [],
  };

  log(`\n${CYAN}=== Executing Assignments ===${RESET}\n`);

  for (const assignment of assignments.assignments) {
    try {
      // Verify order exists and is pending
      const order = orderStore.read(assignment.orderId);
      if (!order) {
        log(
          `${YELLOW}[Warning]${RESET} Order ${assignment.orderId} not found, skipping`,
        );
        continue;
      }
      if (order.status !== "pending") {
        log(
          `${YELLOW}[Warning]${RESET} Order ${assignment.orderId} is not pending (status: ${order.status}), skipping`,
        );
        continue;
      }

      // Verify driver exists and is available
      const driver = driverStore.read(assignment.driverId);
      if (!driver) {
        log(
          `${YELLOW}[Warning]${RESET} Driver ${assignment.driverId} not found, skipping`,
        );
        continue;
      }
      if (driver.status !== "available") {
        log(
          `${YELLOW}[Warning]${RESET} Driver ${assignment.driverId} is not available (status: ${driver.status}), skipping`,
        );
        continue;
      }

      // Update order with assigned driver
      orderStore.update(assignment.orderId, {
        assignedDriverId: assignment.driverId,
        status: "confirmed",
      });

      // Update driver status to busy
      driverStore.update(assignment.driverId, { status: "busy" });

      const timestamp = new Date().toISOString();
      workflowLog.assignments.push({
        orderId: assignment.orderId,
        driverId: assignment.driverId,
        timestamp,
      });

      log(
        `${GREEN}✓${RESET} Assigned order ${assignment.orderId} to driver ${driver.name} (${assignment.driverId})`,
      );
      log(`  ${CYAN}Reasoning:${RESET} ${assignment.reasoning}`);

      workflowLog.assignmentsMade++;
    } catch (error) {
      log(
        `${YELLOW}[Error]${RESET} Failed to assign order ${assignment.orderId}: ${(error as Error).message}`,
      );
    }
    workflowLog.ordersProcessed++;
  }

  workflowLog.status = "completed";
  workflowLog.completedAt = new Date().toISOString();

  return workflowLog;
}

// ============================================================================
// Main Workflow
// ============================================================================

async function runAssignmentWorkflow(): Promise<WorkflowOutput> {
  log(`\n${CYAN}=== Order Assignment Workflow ===${RESET}\n`);

  // Get pending orders and available drivers
  const pendingOrders = orderStore.list({ status: "pending" });
  const availableDrivers = driverStore.list({ status: "available" });

  log(`${BLUE}[Info]${RESET} Found ${pendingOrders.length} pending orders`);
  log(`${BLUE}[Info]${RESET} Found ${availableDrivers.length} available drivers`);

  if (pendingOrders.length === 0) {
    log(`${YELLOW}[Info]${RESET} No pending orders to assign`);
    return {
      totalOrders: 0,
      totalDrivers: availableDrivers.length,
      assignments: [],
      summary: "No pending orders found. Workflow completed with no assignments.",
    };
  }

  if (availableDrivers.length === 0) {
    log(`${YELLOW}[Warning]${RESET} No available drivers to assign orders to`);
    return {
      totalOrders: pendingOrders.length,
      totalDrivers: 0,
      assignments: [],
      summary: `${pendingOrders.length} pending orders found, but no available drivers. No assignments made.`,
    };
  }

  // Prepare context for the AI
  const ordersContext = pendingOrders
    .map(
      (o) =>
        `- Order ${o.id}: Customer ${o.customerSnapshot.name} at ${o.customerSnapshot.address}, ${o.items.length} items, $${o.totalAmount.toFixed(2)}`,
    )
    .join("\n");

  const driversContext = availableDrivers
    .map((d) => `- Driver ${d.id}: ${d.name} (status: ${d.status})`)
    .join("\n");

  const { $schema: _, ...schema } = z.toJSONSchema(WorkflowOutputSchema);

  const prompt = `You are an order assignment system for BurritoOps, a burrito delivery service.

Your task is to assign pending orders to available drivers efficiently.

PENDING ORDERS:
${ordersContext}

AVAILABLE DRIVERS:
${driversContext}

ASSIGNMENT RULES:
1. Each driver can only be assigned ONE order at a time
2. Prioritize orders by creation time (oldest first)
3. Consider delivery addresses when assigning (though detailed routing is not required)
4. Provide reasoning for each assignment

Create the optimal assignment plan. Assign as many orders as possible, up to the number of available drivers.`;

  const conversation = query({
    prompt,
    options: {
      outputFormat: { type: "json_schema", schema },
    },
  });

  let output: WorkflowOutput | undefined;

  for await (const msg of conversation) {
    logEvent(msg);
    printEvent(msg);

    if (msg.type === "result" && msg.subtype === "success") {
      output = (msg as any).structured_output;
    }
  }

  if (!output) {
    throw new Error("Assignment workflow failed to produce output");
  }

  return output;
}

// ============================================================================
// Main Entry Point
// ============================================================================

async function main() {
  log(`${BLUE}╔════════════════════════════════════════╗${RESET}`);
  log(`${BLUE}║   🌯 BurritoOps Assignment Workflow   ║${RESET}`);
  log(`${BLUE}╚════════════════════════════════════════╝${RESET}`);
  log(`${CYAN}[System]${RESET} Workflow log: ${WORKFLOW_LOG_PATH}`);
  log(`${CYAN}[System]${RESET} Events log: ${EVENTS_LOG_PATH}\n`);

  let workflowLog: AssignmentLog = {
    workflowId: SESSION_TS,
    status: "in_progress",
    startedAt: new Date().toISOString(),
    ordersProcessed: 0,
    assignmentsMade: 0,
    assignments: [],
  };

  try {
    // Run the AI-powered assignment workflow
    const output = await runAssignmentWorkflow();

    // Execute the assignments
    workflowLog = executeAssignments(output);

    // Save final log
    saveWorkflowLog(workflowLog);

    // Print summary
    log(`\n${CYAN}=== Workflow Summary ===${RESET}`);
    log(output.summary);
    log(
      `\n${GREEN}✓${RESET} Workflow completed: ${workflowLog.assignmentsMade} assignments made`,
    );
    log(`${BLUE}[Info]${RESET} Logs saved to ${WORKFLOW_LOG_PATH}`);
  } catch (error) {
    workflowLog.status = "error";
    workflowLog.error = { message: (error as Error).message };
    workflowLog.completedAt = new Date().toISOString();
    saveWorkflowLog(workflowLog);

    log(`\n${YELLOW}[Error]${RESET} Workflow failed: ${(error as Error).message}`);
    throw error;
  }
}

main();
