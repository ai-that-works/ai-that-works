import { existsSync, mkdirSync, writeFileSync, appendFileSync } from "node:fs";
import { query, type SDKMessage } from "./agent-sdk";
import { z } from "zod";
import { BLUE, CYAN, GREEN, YELLOW, RESET, log, printEvent } from "./utils";
import { orderStore } from "./store/order-store";
import { driverStore } from "./store/driver-store";

// ============================================================================
// Dashboard Log - Persisted State
// ============================================================================

interface DashboardSnapshot {
  timestamp: string;
  orders: {
    total: number;
    byStatus: Record<string, number>;
    totalRevenue: number;
    averageOrderValue: number;
  };
  drivers: {
    total: number;
    available: number;
    busy: number;
    offline: number;
  };
  metrics: {
    ordersPerDriver: number;
    revenuePerDriver: number;
    utilizationRate: number;
  };
}

const LOGS_DIR = "logs";
const SESSION_TS = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const DASHBOARD_LOG_PATH = `${LOGS_DIR}/dashboard-snapshot-${SESSION_TS}.json`;
const EVENTS_LOG_PATH = `${LOGS_DIR}/dashboard-events-${SESSION_TS}.jsonl`;

if (!existsSync(LOGS_DIR)) mkdirSync(LOGS_DIR, { recursive: true });

function saveDashboardSnapshot(snapshot: DashboardSnapshot) {
  writeFileSync(DASHBOARD_LOG_PATH, JSON.stringify(snapshot, null, 2));
  log(`${BLUE}[Saved]${RESET} ${DASHBOARD_LOG_PATH}`);
}

function logEvent(event: SDKMessage) {
  appendFileSync(EVENTS_LOG_PATH, JSON.stringify(event) + "\n");
}

// ============================================================================
// Dashboard Schema
// ============================================================================

const DashboardOutputSchema = z.object({
  overview: z
    .string()
    .describe("A friendly, conversational overview of the system status"),
  orderSummary: z
    .string()
    .describe("Summary of order statistics with key insights"),
  driverSummary: z
    .string()
    .describe("Summary of driver status with utilization insights"),
  metricsSummary: z
    .string()
    .describe("Summary of key performance metrics"),
  recommendations: z
    .array(z.string())
    .describe("Actionable recommendations based on current state"),
  alertsOrIssues: z
    .array(z.string())
    .describe("Any alerts or issues that need attention"),
});

type DashboardOutput = z.infer<typeof DashboardOutputSchema>;

// ============================================================================
// Data Collection
// ============================================================================

function collectDashboardData(): DashboardSnapshot {
  const allOrders = orderStore.list();
  const allDrivers = driverStore.list();

  // Orders by status
  const byStatus: Record<string, number> = {};
  let totalRevenue = 0;

  for (const order of allOrders) {
    byStatus[order.status] = (byStatus[order.status] || 0) + 1;
    totalRevenue += order.totalAmount;
  }

  // Driver counts
  const availableDrivers = allDrivers.filter((d) => d.status === "available");
  const busyDrivers = allDrivers.filter((d) => d.status === "busy");
  const offlineDrivers = allDrivers.filter((d) => d.status === "offline");

  // Calculate metrics
  const totalDrivers = allDrivers.length;
  const activeDrivers = availableDrivers.length + busyDrivers.length;
  const utilizationRate =
    activeDrivers > 0 ? (busyDrivers.length / activeDrivers) * 100 : 0;
  const ordersPerDriver = totalDrivers > 0 ? allOrders.length / totalDrivers : 0;
  const revenuePerDriver = totalDrivers > 0 ? totalRevenue / totalDrivers : 0;
  const averageOrderValue = allOrders.length > 0 ? totalRevenue / allOrders.length : 0;

  return {
    timestamp: new Date().toISOString(),
    orders: {
      total: allOrders.length,
      byStatus,
      totalRevenue,
      averageOrderValue,
    },
    drivers: {
      total: totalDrivers,
      available: availableDrivers.length,
      busy: busyDrivers.length,
      offline: offlineDrivers.length,
    },
    metrics: {
      ordersPerDriver,
      revenuePerDriver,
      utilizationRate,
    },
  };
}

// ============================================================================
// Dashboard Generation
// ============================================================================

async function generateDashboard(
  snapshot: DashboardSnapshot,
): Promise<DashboardOutput> {
  log(`\n${CYAN}=== Generating Dashboard ===${RESET}\n`);

  const { $schema: _, ...schema } = z.toJSONSchema(DashboardOutputSchema);

  // Format the data for the AI
  const ordersByStatusText = Object.entries(snapshot.orders.byStatus)
    .map(([status, count]) => `  - ${status}: ${count}`)
    .join("\n");

  const prompt = `You are the BurritoOps dashboard system, providing insights and analytics for a burrito delivery service.

Generate a comprehensive dashboard report based on the following data:

ORDERS:
- Total Orders: ${snapshot.orders.total}
- Total Revenue: $${snapshot.orders.totalRevenue.toFixed(2)}
- Average Order Value: $${snapshot.orders.averageOrderValue.toFixed(2)}
- Orders by Status:
${ordersByStatusText}

DRIVERS:
- Total Drivers: ${snapshot.drivers.total}
- Available: ${snapshot.drivers.available}
- Busy: ${snapshot.drivers.busy}
- Offline: ${snapshot.drivers.offline}

METRICS:
- Orders per Driver: ${snapshot.metrics.ordersPerDriver.toFixed(2)}
- Revenue per Driver: $${snapshot.metrics.revenuePerDriver.toFixed(2)}
- Driver Utilization Rate: ${snapshot.metrics.utilizationRate.toFixed(1)}%

TASK:
1. Provide a friendly overview of the current system status
2. Summarize order statistics with key insights
3. Summarize driver status and utilization
4. Highlight key performance metrics
5. Provide 2-4 actionable recommendations based on the data
6. Note any alerts or issues (e.g., too many pending orders, no available drivers, low utilization)

Be conversational, insightful, and focus on actionable information.`;

  const conversation = query({
    prompt,
    options: {
      outputFormat: { type: "json_schema", schema },
    },
  });

  let output: DashboardOutput | undefined;

  for await (const msg of conversation) {
    logEvent(msg);
    printEvent(msg);

    if (msg.type === "result" && msg.subtype === "success") {
      output = (msg as any).structured_output;
    }
  }

  if (!output) {
    throw new Error("Dashboard generation failed to produce output");
  }

  return output;
}

// ============================================================================
// Display Dashboard
// ============================================================================

function displayDashboard(output: DashboardOutput, snapshot: DashboardSnapshot) {
  log(`\n${BLUE}╔════════════════════════════════════════════════════════════════╗${RESET}`);
  log(`${BLUE}║          🌯 BurritoOps System Dashboard 🌯                    ║${RESET}`);
  log(`${BLUE}╚════════════════════════════════════════════════════════════════╝${RESET}`);
  log(`${CYAN}[Snapshot Time]${RESET} ${new Date(snapshot.timestamp).toLocaleString()}\n`);

  // Overview
  log(`${GREEN}━━━ Overview ━━━${RESET}`);
  log(output.overview);
  log("");

  // Orders
  log(`${GREEN}━━━ Order Summary ━━━${RESET}`);
  log(output.orderSummary);
  log("");

  // Drivers
  log(`${GREEN}━━━ Driver Summary ━━━${RESET}`);
  log(output.driverSummary);
  log("");

  // Metrics
  log(`${GREEN}━━━ Key Metrics ━━━${RESET}`);
  log(output.metricsSummary);
  log("");

  // Recommendations
  if (output.recommendations.length > 0) {
    log(`${GREEN}━━━ Recommendations ━━━${RESET}`);
    output.recommendations.forEach((rec, idx) => {
      log(`${CYAN}${idx + 1}.${RESET} ${rec}`);
    });
    log("");
  }

  // Alerts
  if (output.alertsOrIssues.length > 0) {
    log(`${YELLOW}━━━ Alerts & Issues ━━━${RESET}`);
    output.alertsOrIssues.forEach((alert) => {
      log(`${YELLOW}⚠${RESET}  ${alert}`);
    });
    log("");
  }

  log(`${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}`);
  log(`${CYAN}[Raw Data]${RESET} Snapshot saved to: ${DASHBOARD_LOG_PATH}`);
}

// ============================================================================
// Main Entry Point
// ============================================================================

async function main() {
  log(`${BLUE}╔════════════════════════════════════════╗${RESET}`);
  log(`${BLUE}║      🌯 BurritoOps Dashboard 🌯       ║${RESET}`);
  log(`${BLUE}╚════════════════════════════════════════╝${RESET}`);
  log(`${CYAN}[System]${RESET} Generating dashboard...\n`);

  try {
    // Collect current system data
    const snapshot = collectDashboardData();

    // Save snapshot
    saveDashboardSnapshot(snapshot);

    // Generate AI-powered dashboard
    const output = await generateDashboard(snapshot);

    // Display the dashboard
    displayDashboard(output, snapshot);

    log(`\n${GREEN}✓${RESET} Dashboard generation completed`);
    log(`${BLUE}[Info]${RESET} Logs saved to ${DASHBOARD_LOG_PATH}`);
  } catch (error) {
    log(`\n${YELLOW}[Error]${RESET} Dashboard generation failed: ${(error as Error).message}`);
    throw error;
  }
}

main();
