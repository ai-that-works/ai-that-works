import asyncio
import threading
import time

from dotenv import load_dotenv
import os

from runtime import InMemoryAgentSystem, Message


async def main() -> None:
    query = input("What would you like to research? ")

    # Start in-memory agent
    system = InMemoryAgentSystem()
    convo_id = "default"
    runtime = system.start(convo_id, query)

    # Renderer thread: prints events as they arrive
    print_lock = threading.RLock()

    def render_loop() -> None:
        last_index = 0
        while not system.is_done(convo_id):
            with runtime.events_cv:
                runtime.events_cv.wait(timeout=0.25)
                events = list(runtime.events)
            # Print new events
            with print_lock:
                for evt in events[last_index:]:
                    print(f"[{evt.event_type}] {evt.message}")
                last_index = len(events)
        # Flush any remaining events
        with print_lock:
            with runtime.events_cv:
                for evt in list(runtime.events)[last_index:]:
                    print(f"[{evt.event_type}] {evt.message}")

    t = threading.Thread(target=render_loop, daemon=True)
    t.start()

    # Input loop for interruptions
    print("Type: 'info <text>', 'replan <text>', or 'cancel'. Press Enter to send.")
    while not system.is_done(convo_id):
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, input, "> ")
        except (EOFError, KeyboardInterrupt):
            system.cancel(convo_id)
            break
        line = line.strip()
        if not line:
            continue
        if line.lower() == "cancel":
            system.cancel(convo_id)
            continue
        if line.startswith("replan "):
            system.queue(convo_id, Message(kind="replan", text=line[len("replan "):].strip()))
        elif line.startswith("info "):
            system.queue(convo_id, Message(kind="info", text=line[len("info "):].strip()))
        else:
            # default to info
            system.queue(convo_id, Message(kind="info", text=line))

    # Wait a moment for renderer to flush
    time.sleep(0.2)


if __name__ == "__main__":
    os.environ["BAML_LOG"] = "error"
    load_dotenv("../.env")
    asyncio.run(main())
