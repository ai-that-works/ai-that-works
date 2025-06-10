class Code {
    title string @description(#"
        goal of the lesson
    "#)
    code string 
    @description(#"
        use triple backticks to format the code
        {
           code: ```python
           ...
           ```
        }
    "#)
}

function GenerateCode(input: string) -> Code[] {
  client CustomSonnet

  prompt #"
    Generate code for the following input as a lesson with diffs.

    {{ ctx.output_format }}

    Before answering, make a plan for how to incrementally build the code.

    example:
    section 1:
    ...
    section 2:
    ...
    section 3:
    ...
    ...

    [ .. ]

    {{ _.role('user') }}
    {{ input }}
  "#
}

test TestName {
  functions [GenerateCode]
  args {
    input #"
      a sorting algorithm with merge sort
    "#
  }
}


test TestName2 {
  functions [GenerateCode]
  args {
    input #"
      create a kubenetes operator to spin up RDS instances in go lang
    "#
  }
}
