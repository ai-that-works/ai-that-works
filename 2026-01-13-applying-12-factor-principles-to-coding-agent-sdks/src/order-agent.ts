import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";
import { existsSync, mkdirSync, appendFileSync } from "node:fs";
import { query, type SDKMessage, type SDKUserMessage } from "./agent-sdk";
import { z } from "zod";
import {
  BLUE,
  CYAN,
  GREEN,
  YELLOW,
  RESET,
  createInputQueue,
  log,
  printEvent,
} from "./utils";
import { orderStore } from "./store/order-store";
import { OrderStatusSchema, createMenuItem, createCustomer } from "./models/types";

// ============================================================================
// Event Logging
// ============================================================================

const LOGS_DIR = "logs";
const SESSION_TS = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const EVENTS_LOG_PATH = `${LOGS_DIR}/order-agent-${SESSION_TS}.jsonl`;

if (!existsSync(LOGS_DIR)) mkdirSync(LOGS_DIR, { recursive: true });

function logEvent(event: SDKMessage) {
  appendFileSync(EVENTS_LOG_PATH, JSON.stringify(event) + "\n");
}

// ============================================================================
// Agent Action Schema
// ============================================================================

const AgentActionSchema = z.object({
  action: z.enum([
    "create_order",
    "list_orders",
    "view_order",
    "update_status",
    "help",
    "exit",
  ]),
  reasoning: z.string().describe("Brief explanation of why this action was chosen"),
  parameters: z
    .object({
      orderId: z.string().optional(),
      customerName: z.string().optional(),
      customerPhone: z.string().optional(),
      customerAddress: z.string().optional(),
      items: z
        .array(
          z.object({
            name: z.string(),
            price: z.number(),
            quantity: z.number(),
            description: z.string().optional(),
          }),
        )
        .optional(),
      notes: z.string().optional(),
      status: OrderStatusSchema.optional(),
      filter: z
        .object({
          status: OrderStatusSchema.optional(),
          customerId: z.string().optional(),
        })
        .optional(),
    })
    .optional(),
  message: z.string().describe("Message to display to the user"),
});

type AgentAction = z.infer<typeof AgentActionSchema>;

// ============================================================================
// Order Management Actions
// ============================================================================

function executeAction(action: AgentAction): string {
  try {
    switch (action.action) {
      case "create_order": {
        const params = action.parameters;
        if (
          !params?.customerName ||
          !params?.customerPhone ||
          !params?.customerAddress ||
          !params?.items ||
          params.items.length === 0
        ) {
          return "Error: Missing required parameters for creating an order. Need customer name, phone, address, and at least one item.";
        }

        const customer = createCustomer(
          params.customerName,
          params.customerPhone,
          params.customerAddress,
        );

        const orderItems = params.items.map((item) => ({
          menuItem: createMenuItem(
            item.name,
            item.price,
            item.description || `Delicious ${item.name}`,
          ),
          quantity: item.quantity,
        }));

        const order = orderStore.create(customer, orderItems, params.notes);

        return `✅ Order created successfully!\n\nOrder ID: ${order.id}\nCustomer: ${customer.name}\nTotal: $${order.totalAmount.toFixed(2)}\nStatus: ${order.status}\nItems:\n${order.items
          .map(
            (item) =>
              `  - ${item.menuItemSnapshot.name} x${item.quantity} ($${item.menuItemSnapshot.price.toFixed(2)} each)`,
          )
          .join("\n")}`;
      }

      case "list_orders": {
        const orders = orderStore.list(action.parameters?.filter);

        if (orders.length === 0) {
          return "No orders found.";
        }

        return `📋 Orders (${orders.length} total):\n\n${orders
          .map(
            (order) =>
              `Order #${order.id}\n  Customer: ${order.customerSnapshot.name}\n  Status: ${order.status}\n  Total: $${order.totalAmount.toFixed(2)}\n  Created: ${new Date(order.createdAt).toLocaleString()}\n  Items: ${order.items.length} item(s)`,
          )
          .join("\n\n")}`;
      }

      case "view_order": {
        if (!action.parameters?.orderId) {
          return "Error: Order ID is required.";
        }

        const order = orderStore.read(action.parameters.orderId);
        if (!order) {
          return `Error: Order not found: ${action.parameters.orderId}`;
        }

        return `📦 Order Details\n\nOrder ID: ${order.id}\nStatus: ${order.status}\nCreated: ${new Date(order.createdAt).toLocaleString()}\nUpdated: ${new Date(order.updatedAt).toLocaleString()}\n\nCustomer:\n  Name: ${order.customerSnapshot.name}\n  Phone: ${order.customerSnapshot.phone}\n  Address: ${order.customerSnapshot.address}\n\nItems:\n${order.items
          .map(
            (item) =>
              `  - ${item.menuItemSnapshot.name} x${item.quantity}\n    Price: $${item.menuItemSnapshot.price.toFixed(2)} each\n    Subtotal: $${(item.menuItemSnapshot.price * item.quantity).toFixed(2)}`,
          )
          .join("\n")}

Total: $${order.totalAmount.toFixed(2)}${order.assignedDriverId ? `\nAssigned Driver: ${order.assignedDriverId}` : ""}${order.notes ? `\nNotes: ${order.notes}` : ""}`;
      }

      case "update_status": {
        if (!action.parameters?.orderId || !action.parameters?.status) {
          return "Error: Order ID and status are required.";
        }

        const order = orderStore.update(action.parameters.orderId, {
          status: action.parameters.status,
        });

        return `✅ Order status updated!\n\nOrder ID: ${order.id}\nNew Status: ${order.status}\nUpdated: ${new Date(order.updatedAt).toLocaleString()}`;
      }

      case "help": {
        return `🌯 BurritoOps Order Management Agent

Available Commands:
  • create order - Create a new order with customer info and items
  • list orders - View all orders (optionally filter by status)
  • view order - View detailed information about a specific order
  • update status - Change the status of an order
  • help - Show this help message
  • exit - Quit the agent

Examples:
  "Create an order for John Doe, phone 555-1234, address 123 Main St, with 2 burritos at $12 each"
  "List all pending orders"
  "Show me order details for ord-123"
  "Update order ord-123 status to confirmed"`;
      }

      case "exit": {
        return "Goodbye! 🌯";
      }

      default:
        return "Unknown action.";
    }
  } catch (error) {
    return `Error executing action: ${(error as Error).message}`;
  }
}

// ============================================================================
// Main Agent Loop
// ============================================================================

async function main() {
  const rl = createInterface({ input: stdin, output: stdout });

  log(`${BLUE}╔════════════════════════════════════════╗${RESET}`);
  log(`${BLUE}║   🌯 BurritoOps Order Management 🌯   ║${RESET}`);
  log(`${BLUE}╚════════════════════════════════════════╝${RESET}`);
  log(`${CYAN}[System]${RESET} Events log: ${EVENTS_LOG_PATH}`);
  log(`${CYAN}[System]${RESET} Type 'help' for available commands, 'exit' to quit\n`);

  const inputQueue = createInputQueue<string>();
  const { $schema: _, ...schema } = z.toJSONSchema(AgentActionSchema);

  let sessionId = "";

  const systemPrompt = `You are BurritoOps, an AI agent that helps manage burrito delivery orders.

You have access to an order management system with the following capabilities:
- Create new orders with customer information and menu items
- List all orders (with optional filtering)
- View detailed information about specific orders
- Update order status

When the user makes a request, analyze it and choose the appropriate action. Always provide clear, helpful messages to the user.

Order Status Flow:
pending → confirmed → preparing → ready → out_for_delivery → delivered
(or cancelled at any point)

Be conversational and helpful. If the user's request is unclear, ask for clarification.`;

  // Start with the initial prompt
  inputQueue.push(systemPrompt);

  const messageGenerator = async function* (): AsyncIterable<SDKUserMessage> {
    while (true) {
      const input = await inputQueue.pull();
      if (input === null) return;
      yield {
        type: "user",
        session_id: sessionId,
        parent_tool_use_id: null,
        message: { role: "user", content: input },
      };
    }
  };

  const conversation = query({
    prompt: messageGenerator(),
    options: {
      outputFormat: { type: "json_schema", schema },
    },
  });

  for await (const msg of conversation) {
    logEvent(msg);
    printEvent(msg);

    if (msg.type === "system" && msg.subtype === "init") {
      sessionId = msg.session_id;
    }

    if (msg.type === "result" && msg.subtype === "success") {
      const action = (msg as any).structured_output as AgentAction | undefined;

      if (action) {
        // Display reasoning
        log(`${CYAN}[Reasoning]${RESET} ${action.reasoning}`);

        // Execute the action
        const result = executeAction(action);

        // Display result
        log(`\n${YELLOW}[Agent]${RESET} ${action.message}`);
        if (result) {
          log(`\n${result}\n`);
        }

        // Check for exit
        if (action.action === "exit") {
          inputQueue.close();
          rl.close();
          break;
        }

        // Get next user input (only if not exiting)
        try {
          const userInput = await rl.question(`${GREEN}>${RESET} `);
          if (!userInput || userInput.toLowerCase() === "exit") {
            log(`${CYAN}[System]${RESET} Exiting...`);
            inputQueue.push("The user wants to exit. Set action to 'exit'.");
          } else {
            log(`${GREEN}[User]${RESET} ${userInput}`);
            inputQueue.push(userInput);
          }
        } catch (error) {
          // Readline closed (e.g., piped input ended), gracefully exit
          log(`${CYAN}[System]${RESET} Input closed, exiting...`);
          inputQueue.push("The user's input stream closed. Set action to 'exit'.");
        }
      }
    }
  }

  rl.close();
  log(`\n${BLUE}[System]${RESET} Session ended. Logs saved to ${EVENTS_LOG_PATH}`);
}

main();
