# Chapter 0 - Hello World

Let's start with a basic TypeScript setup and a hello world program.

This guide is written in TypeScript (yes, a python version is coming soon)

There are many checkpoints between the every file edit in theworkshop steps, 
so even if you aren't super familiar with typescript,
you should be able to keep up and run each example.

To run this guide, you'll need a relatively recent version of nodejs and npm installed

You can use whatever nodejs version manager you want, [homebrew](https://formulae.brew.sh/formula/node) is fine


    brew install node@20

You should see the node version

    node --version

Copy initial package.json

    cp ./walkthrough/00-package.json package.json

Install dependencies

    npm install

Copy tsconfig.json

    cp ./walkthrough/00-tsconfig.json tsconfig.json

add .gitignore

    cp ./walkthrough/00-.gitignore .gitignore

Create src folder

    mkdir -p src

Add a simple hello world index.ts

    cp ./walkthrough/00-index.ts src/index.ts

Run it to verify

    npx tsx src/index.ts

You should see:

    hello, world!


# Chapter 1 - CLI and Agent Loop

Now let's add BAML and create our first agent with a CLI interface.

First, we'll need to install [BAML](https://github.com/boundaryml/baml)
which is a tool for prompting and structured outputs.


    npm install @boundaryml/baml

Initialize BAML

    npx baml-cli init

Remove default resume.baml

    rm baml_src/resume.baml

Add our starter agent, a single baml prompt that we'll build on

    cp ./walkthrough/01-agent.baml baml_src/agent.baml

Generate BAML client code

    npx baml-cli generate

Enable BAML logging for this section

    export BAML_LOG=debug

Add the CLI interface

    cp ./walkthrough/01-cli.ts src/cli.ts

Update index.ts to use the CLI

    cp ./walkthrough/01-index.ts src/index.ts

Add the agent implementation

    cp ./walkthrough/01-agent.ts src/agent.ts

The the BAML code is configured to use BASETEN_API_KEY by default

To get a Baseten API key and URL, create an account at [baseten.co](https://baseten.co),
and then deploy [Qwen3 32B from the model library](https://www.baseten.co/library/qwen-3-32b/).

```rust 
  function DetermineNextStep(thread: string) -> DoneForNow {
      client Qwen3
      // ...
```

If you want to run the example with no changes, you can set the BASETEN_API_KEY env var to any valid baseten key.

If you want to try swapping out the model, you can change the `client` line.

[Docs on baml clients can be found here](https://docs.boundaryml.com/guide/baml-basics/switching-llms)

For example, you can configure [gemini](https://docs.boundaryml.com/ref/llm-client-providers/google-ai-gemini) 
or [anthropic](https://docs.boundaryml.com/ref/llm-client-providers/anthropic) as your model provider.

For example, to use openai with an OPENAI_API_KEY, you can do:

    client "openai/gpt-4o"


Set your env vars

    export BASETEN_API_KEY=...
export BASETEN_BASE_URL=...

Try it out

    npx tsx src/index.ts hello

you should see a familiar response from the model

    {
      intent: 'done_for_now',
      message: 'Hello! How can I assist you today?'
    }


# Chapter 2 - Add Calculator Tools

Let's add some calculator tools to our agent.

Let's start by adding a tool definition for the calculator

These are simpile structured outputs that we'll ask the model to 
return as a "next step" in the agentic loop.


    cp ./walkthrough/02-tool_calculator.baml baml_src/tool_calculator.baml

Now, let's update the agent's DetermineNextStep method to
expose the calculator tools as potential next steps


    cp ./walkthrough/02-agent.baml baml_src/agent.baml

Generate updated BAML client

    npx baml-cli generate

Try out the calculator

    npx tsx src/index.ts 'can you add 3 and 4'

You should see a tool call to the calculator

    {
      intent: 'add',
      a: 3,
      b: 4
    }


# Chapter 3 - Process Tool Calls in a Loop

Now let's add a real agentic loop that can run the tools and get a final answer from the LLM.

First, lets update the agent to handle the tool call


    cp ./walkthrough/03-agent.ts src/agent.ts

Now, lets try it out


    npx tsx src/index.ts 'can you add 3 and 4'

you should see the agent call the tool and then return the result

    {
      intent: 'done_for_now',
      message: 'The sum of 3 and 4 is 7.'
    }

For the next step, we'll do a more complex calculation, let's turn off the baml logs for more concise output

    export BAML_LOG=off

Try a multi-step calculation

    npx tsx src/index.ts 'can you add 3 and 4, then add 6 to that result'

you'll notice that tools like multiply and divide are not available

    npx tsx src/index.ts 'can you multiply 3 and 4'

next, let's add handlers for the rest of the calculator tools


    cp ./walkthrough/03b-agent.ts src/agent.ts

Test subtraction

    npx tsx src/index.ts 'can you subtract 3 from 4'

now, let's test the multiplication tool


    npx tsx src/index.ts 'can you multiply 3 and 4'

finally, let's test a more complex calculation with multiple operations


    npx tsx src/index.ts 'can you multiply 3 and 4, then divide the result by 2 and then add 12 to that result'

congratulations, you've taking your first step into hand-rolling an agent loop.

from here, we're going to start incorporating some more intermediate and advanced
concepts for 12-factor agents.



# Chapter 4 - Add Tests to agent.baml

Let's add some tests to our BAML agent.

to start, leave the baml logs enabled

    export BAML_LOG=debug

next, let's add some tests to the agent

We'll start with a simple test that checks the agent's ability to handle
a basic calculation.


    cp ./walkthrough/04-agent.baml baml_src/agent.baml

Run the tests

    npx baml-cli test

now, let's improve the test with assertions!

Assertions are a great way to make sure the agent is working as expected,
and can easily be extended to check for more complex behavior.


    cp ./walkthrough/04b-agent.baml baml_src/agent.baml

Run the tests

    npx baml-cli test

as you add more tests, you can disable the logs to keep the output clean.
You may want to turn them on as you iterate on specific tests.


    export BAML_LOG=off

now, let's add some more complex test cases,
where we resume from in the middle of an in-progress
agentic context window


    cp ./walkthrough/04c-agent.baml baml_src/agent.baml

let's try to run it


    npx baml-cli test


# Chapter 5 - Multiple Human Tools

In this section, we'll add support for multiple tools that serve to
contact humans.


for this section, we'll disable the baml logs. You can optionally enable them if you want to see more details.

    export BAML_LOG=off

first, let's add a tool that can request clarification from a human

this will be different from the "done_for_now" tool,
and can be used to more flexibly handle different types of human interactions
in your agent.


    cp ./walkthrough/05-agent.baml baml_src/agent.baml

next, let's re-generate the client code

NOTE - if you're using the VSCode extension for BAML,
the client will be regenerated automatically when you save the file
in your editor.


    npx baml-cli generate

now, let's update the agent to use the new tool


    cp ./walkthrough/05-agent.ts src/agent.ts

next, let's update the CLI to handle clarification requests
by requesting input from the user on the CLI


    cp ./walkthrough/05-cli.ts src/cli.ts

let's try it out


    npx tsx src/index.ts 'can you multiply 3 and FD*(#F&& '

next, let's add a test that checks the agent's ability to handle
a clarification request


    cp ./walkthrough/05b-agent.baml baml_src/agent.baml

and now we can run the tests again


    npx baml-cli test

you'll notice the new test passes, but the hello world test fails

This is because the agent's default behavior is to return "done_for_now"


    cp ./walkthrough/05c-agent.baml baml_src/agent.baml

Verify tests pass

    npx baml-cli test


# Chapter 6 - Customize Your Prompt with Reasoning

In this section, we'll explore how to customize the prompt of the agent
with reasoning steps.

this is core to [factor 2 - own your prompts](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-2-own-your-prompts.md)

there's a deep dive on reasoning on AI That Works [reasoning models versus reasoning steps](https://github.com/hellovai/ai-that-works/tree/main/2025-04-07-reasoning-models-vs-prompts)


for this section, it will be helpful to leave the baml logs enabled

    export BAML_LOG=debug

update the agent prompt to include a reasoning step


    cp ./walkthrough/06-agent.baml baml_src/agent.baml

generate the updated client

    npx baml-cli generate

now, you can try it out with a simple prompt


    npx tsx src/index.ts 'can you multiply 3 and 4'

you should see output from the baml logs showing the reasoning steps

#### optional challenge

add a field to your tool output format that includes the reasoning steps in the output!



# Chapter 7 - Customize Your Context Window

In this section, we'll explore how to customize the context window
of the agent.

this is core to [factor 3 - own your context window](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-3-own-your-context-window.md)


update the agent to pretty-print the Context window for the model


    cp ./walkthrough/07-agent.ts src/agent.ts

Test the formatting

    BAML_LOG=info npx tsx src/index.ts 'can you multiply 3 and 4, then divide the result by 2 and then add 12 to that result'

next, let's update the agent to use XML formatting instead

this is a very popular format for passing data to a model,

among other things, because of the token efficiency of XML.


    cp ./walkthrough/07b-agent.ts src/agent.ts

let's try it out


    BAML_LOG=info npx tsx src/index.ts 'can you multiply 3 and 4, then divide the result by 2 and then add 12 to that result'

lets update our tests to match the new output format


    cp ./walkthrough/07c-agent.baml baml_src/agent.baml

check out the updated tests


    npx baml-cli test


# Chapter 8 - Adding API Endpoints

Add an Express server to expose the agent via HTTP.

for this section, we'll disable the baml logs. You can optionally enable them if you want to see more details.

    export BAML_LOG=off

Install Express and types

    npm install express && npm install --save-dev @types/express supertest

Add the server implementation

    cp ./walkthrough/08-server.ts src/server.ts

Start the server

    npx tsx src/server.ts

Test with curl (in another terminal)

    curl -X POST http://localhost:3000/thread \
  -H "Content-Type: application/json" \
  -d '{"message":"can you add 3 and 4"}'

You should get an answer from the agent which includes the
agentic trace, ending in a message like:


    {"intent":"done_for_now","message":"The sum of 3 and 4 is 7."}


# Chapter 9 - In-Memory State and Async Clarification

Add state management and async clarification support.

for this section, we'll disable the baml logs. You can optionally enable them if you want to see more details.

    export BAML_LOG=off

Add some simple in-memory state management for threads

    cp ./walkthrough/09-state.ts src/state.ts

update the server to use the state management

* Add thread state management using `ThreadStore`
* return thread IDs and response URLs from the /thread endpoint
* implement GET /thread/:id
* implement POST /thread/:id/response


    cp ./walkthrough/09-server.ts src/server.ts

Start the server

    npx tsx src/server.ts

Test clarification flow

    curl -X POST http://localhost:3000/thread \
  -H "Content-Type: application/json" \
  -d '{"message":"can you multiply 3 and xyz"}'


# Chapter 10 - Adding Human Approval

Add support for human approval of operations.

for this section, we'll disable the baml logs. You can optionally enable them if you want to see more details.

    export BAML_LOG=off

update the server to handle human approvals

* Import `handleNextStep` to execute approved actions
* Add two payload types to distinguish approvals from responses
* Handle responses and approvals differently in the endpoint
* Show better error messages when things go wrongs


    cp ./walkthrough/10-server.ts src/server.ts

Add a few methods to the agent to handle approvals and responses

    cp ./walkthrough/10-agent.ts src/agent.ts

Start the server

    npx tsx src/server.ts

Test division with approval

    curl -X POST http://localhost:3000/thread \
  -H "Content-Type: application/json" \
  -d '{"message":"can you divide 3 by 4"}'

You should see:

    {
      "thread_id": "2b243b66-215a-4f37-8bc6-9ace3849043b",
      "events": [
        {
          "type": "user_input",
          "data": "can you divide 3 by 4"
        },
        {
          "type": "tool_call",
          "data": {
            "intent": "divide",
            "a": 3,
            "b": 4,
            "response_url": "/thread/2b243b66-215a-4f37-8bc6-9ace3849043b/response"
          }
        }
      ]
    }

reject the request with another curl call, changing the thread ID

    curl -X POST 'http://localhost:3000/thread/{thread_id}/response' \
  -H "Content-Type: application/json" \
  -d '{"type": "approval", "approved": false, "comment": "I dont think thats right, use 5 instead of 4"}'

You should see: the last tool call is now `"intent":"divide","a":3,"b":5`

    {
      "events": [
        {
          "type": "user_input",
          "data": "can you divide 3 by 4"
        },
        {
          "type": "tool_call",
          "data": {
            "intent": "divide",
            "a": 3,
            "b": 4,
            "response_url": "/thread/2b243b66-215a-4f37-8bc6-9ace3849043b/response"
          }
        },
        {
          "type": "tool_response",
          "data": "user denied the operation with feedback: \"I dont think thats right, use 5 instead of 4\""
        },
        {
          "type": "tool_call",
          "data": {
            "intent": "divide",
            "a": 3,
            "b": 5,
            "response_url": "/thread/1f1f5ff5-20d7-4114-97b4-3fc52d5e0816/response"
          }
        }
      ]
    }

now you can approve the operation

    curl -X POST 'http://localhost:3000/thread/{thread_id}/response' \
  -H "Content-Type: application/json" \
  -d '{"type": "approval", "approved": true}'

you should see the final message includes the tool response and final result!

    ...
    {
      "type": "tool_response",
      "data": 0.5
    },
    {
      "type": "done_for_now",
      "message": "I divided 3 by 6 and the result is 0.5. If you have any more operations or queries, feel free to ask!",
      "response_url": "/thread/2b469403-c497-4797-b253-043aae830209/response"
    }


# Chapter 11 - Human Approvals over email

in this section, we'll add support for human approvals over email.

This will start a little bit contrived, just to get the concepts down -

We'll start by invoking the workflow from the CLI but approvals for `divide`
and `request_more_information` will be handled over email,
then the final `done_for_now` answer will be printed back to the CLI

While contrived, this is a great example of the flexibility you get from
[factor 7 - contact humans with tools](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-7-contact-humans-with-tools.md)


for this section, we'll disable the baml logs. You can optionally enable them if you want to see more details.

    export BAML_LOG=off

Install HumanLayer

    npm install humanlayer

Update CLI to send `divide` and `request_more_information` to a human via email

    cp ./walkthrough/11-cli.ts src/cli.ts

Run the CLI

    npx tsx src/index.ts 'can you divide 4 by 5'

The last line of your program should mention human review step

    nextStep { intent: 'divide', a: 4, b: 5 }
    HumanLayer: Requested human approval from HumanLayer cloud

go ahead and respond to the email with some feedback:

![reject-email](https://github.com/humanlayer/12-factor-agents/blob/main/workshops/2025-05/walkthrough/11-email-reject.png?raw=true)


you should get another email with an updated attempt based on your feedback!

You can go ahead and approve this one:

![appove-email](https://github.com/humanlayer/12-factor-agents/blob/main/workshops/2025-05/walkthrough/11-email-approve.png?raw=true)


and your final output will look like

    nextStep {
     intent: 'done_for_now',
     message: 'The division of 4 by 5 is 0.8. If you have any other calculations or questions, feel free to ask!'
    }
    The division of 4 by 5 is 0.8. If you have any other calculations or questions, feel free to ask!

lets implement the `request_more_information` flow as well


    cp ./walkthrough/11b-cli.ts src/cli.ts

lets test the require_approval flow as by asking for a calculation
with garbled input:


    npx tsx src/index.ts 'can you multiply 4 and xyz'

You should get an email with a request for clarification

    Can you clarify what 'xyz' represents in this context? Is it a specific number, variable, or something else?

you can response with something like

    use 8 instead of xyz

you should see a final result on the CLI like

    I have multiplied 4 and xyz, using the value 8 for xyz, resulting in 32.

as a final step, lets explore using a custom html template for the email


    cp ./walkthrough/11c-cli.ts src/cli.ts

first try with divide:


    npx tsx src/index.ts 'can you divide 4 by 5'

you should see a slightly different email with the custom template

![custom-template-email](https://github.com/humanlayer/12-factor-agents/blob/main/workshops/2025-05/walkthrough/11-email-custom.png?raw=true)

feel free to run with the flow and then you can try updating the template to your liking

(if you're using cursor, something as simple as highlighting the template and asking to "make it better"
should do the trick)

try triggering "request_more_information" as well!


thats it - in the next chapter, we'll build a fully email-driven
workflow agent that uses webhooks for human approval



# Chapter XX - HumanLayer Webhook Integration

the previous sections used the humanlayer SDK in "synchronous mode" - that
means every time we wait for human approval, we sit in a loop
polling until the human response if received.

That's obviously not ideal, especially for production workloads,
so in this section we'll implement [factor 6 - launch / pause / resume with simple APIs](https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-6-launch-pause-resume.md)
by updating the server to end processing after contacting a human, and use webhooks to receive the results.


add code to initialize humanlayer in the server


    cp ./walkthrough/12-1-server-init.ts src/server.ts

next, lets update the /thread endpoint to

1. handle requests asynchronously, returning immediately
2. create a human contact on request_more_information and done_for_now calls


Update the server to be able to handle request_clarification responses

- remove the old /response endpoint and types
- update the /thread endpoint to run processing asynchronously, return immediately
- send a state.threadId when requesting human responses
- add a handleHumanResponse function to process the human response
- add a /webhook endpoint to handle the webhook response


    cp ./walkthrough/12a-server.ts src/server.ts

Start the server in another terminal

    npx tsx src/server.ts

now that the server is running, send a payload to the '/thread' endpoint


__ do the response step

__ now handle approvals for divide

__ now also handle done_for_now

