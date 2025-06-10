class ClarificationRequest {
  intent "request_more_information" @description("you can request more information from me")
  message string
}

class DoneForNow {
  intent "done_for_now"

  message string @description(#"
    message to send to the user about the work that was done. 
  "#)
}
class ProcessRefund {
  intent "process_refund" 
  order_id string
  amount int | float
  reason string
}

type HumanTools = ClarificationRequest | DoneForNow 
type CalculatorTools = AddTool | SubtractTool | MultiplyTool | DivideTool
type CustomerSupportTools = ProcessRefund

function DetermineNextStep(
    thread: string 
) -> HumanTools | CalculatorTools | CustomerSupportTools {
    client "openai/gpt-4o"

    prompt #"
        {{ _.role("system") }}

        You are a helpful assistant that can help with tasks.

        {{ _.role("user") }}

        You are working on the following thread:

        {{ thread }}

        What should the next step be?

        {{ ctx.output_format }}

        Always think about what to do next first, like:

        - ...
        - ...
        - ...

        {...} // schema
    "#
}


test HelloWorld {
  functions [DetermineNextStep]
  args {
    thread #"
      <user_input>
        hello!
      </user_input>
    "#
  }
  @@assert(intent, {{this.intent == "request_more_information"}})
}

test MathOperation {
  functions [DetermineNextStep]
  args {
    thread #"
      <user_input>
        can you multiply 3 and 4?
      </user_input>
    "#
  }
  @@assert(intent, {{this.intent == "multiply"}})
}

test LongMath {
  functions [DetermineNextStep]
  args {
    thread #"
         <user_input>
    can you multiply 3 and 4, then divide the result by 2 and then add 12 to that result?
    </user_input>


    <multiply>
    a: 3
    b: 4
    </multiply>


    <tool_response>
    12
    </tool_response>


    <divide>
    a: 12
    b: 2
    </divide>


    <tool_response>
    6
    </tool_response>


    <add>
    a: 6
    b: 12
    </add>


    <tool_response>
    18
    </tool_response>

    "#
  }
  @@assert(intent, {{this.intent == "done_for_now"}})
  @@assert(answer, {{"18" in this.message}})
}



test MathOperationWithClarification {
  functions [DetermineNextStep]
  args {
    thread #"
          <user_input>
          can you multiply 3 and fe1iiaff10
          </user_input>
      "#
  }
  @@assert(intent, {{this.intent == "request_more_information"}})
}

test MathOperationPostClarification {
  functions [DetermineNextStep]
  args {
    thread #"
        <user_input>
        can you multiply 3 and FD*(#F&& ?
        </user_input>

        <request_more_information>
        message: It seems like there was a typo or mistake in your request. Could you please clarify or provide the correct numbers you would like to multiply?
        </request_more_information>

        <human_response>
        lets try 12 instead
        </human_response>
      "#
  }
  @@assert(intent, {{this.intent == "multiply"}})
  @@assert(b, {{this.a == 3}})
  @@assert(a, {{this.b == 12}})
}
        
test ProcessRefund {
  functions [DetermineNextStep]
  args {
    thread #"
      <user_input>
        can you process a refund for order 1234567890?
      </user_input>
    "#
  }
}


test ProcessRefundWithAllDetails {
  functions [DetermineNextStep]
  args {
    thread #"
      <user_input>
        can you process a refund for order 1234567890?

        its for the jeans they're too big and baggy what is this gen z nonsense?

        they were $200
      </user_input>
    "#
  }
}




test ProcessRefundDenied {
  functions [DetermineNextStep]
  args {
    thread #"
      <user_input>
      i need a refund for oreder 123541 for $200 the jeans are too big and baggy what is this gen z nonsense this is not fashion
      </user_input>

      <process_refund>
      order_id: 123541
      amount: 200
      reason: The jeans are too big and baggy
      </process_refund>

      <tool_response>
      user denied operation process_refund with feedback: can you ask them what color the jeans were first?
      </tool_response>
    "#
  }
  @@assert(intent, {{this.intent == "request_more_information"}})
}