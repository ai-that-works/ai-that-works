class Diff {
    update_notes string[]
    updated_code string[] @description(#"
        use triple backticks to allow for multi-line strings.

        [
            ```diff
                --- my_file.py
                +++ my_file.py
                surrounding_code ...
                - deleted_code ...
                + added_code ...
                surrounding_code ...
            ```
            ```diff
                ...
            ```
        ]
    "#)
}

function FindImports(code: string) -> string[] {
    client Llama8b
    prompt #"
        Find all imports in the code.

        {{ ctx.output_format }}

        {{ _.role('user') }}
        {{ code }}
    "#
}

function GenerateDiff(instructions: string, file_name: string, current_code: string) -> Diff[] {
    client CustomGPT4o
    prompt #"
        {{ instructions }}

        {{ ctx.output_format(prefix="Answer using this schema:\n") }}

        Keep diffs small. can use mutliple diffs for the same file

        {{ _.role('user') }}
        File: {{ file_name }}
        ----
        {{ current_code }}
    "#
}

test TestName {
  functions [FindImports]
  args {
    code #"
        """Core calculator logic handling operations and memory."""

        from operations import add, subtract, multiply, divide
        from dotenv import load_dotenv

        class Calculator:
            def __init__(self):
                self.memory = 0
                self.operations = {
                    '+': add,
                    '-': subtract,
                    '*': multiply,
                    '/': divide
                }
            
            def calculate(self, a: float, operator: str, b: float) -> float:
                """Perform calculation based on operator."""
                if operator not in self.operations:
                    raise ValueError(f"Unknown operator: {operator}")
                
                return self.operations[operator](a, b)
            
            def store_in_memory(self, value: float) -> None:
                """Store a value in memory."""
                self.memory = value
            
            def recall_memory(self) -> float:
                """Recall value from memory."""
                return self.memory
            
            def clear_memory(self) -> None:
                """Clear the memory."""
                self.memory = 0

    "#
  }
}
test TestName {
  functions [GenerateDiff]
  args {
    instructions #"
      add an exponent operation to the calculator
    "#
    file_name #"calculator.py"#
    current_code #"
        """Core calculator logic handling operations and memory."""

        from operations import add, subtract, multiply, divide

        class Calculator:
            def __init__(self):
                self.memory = 0
                self.operations = {
                    '+': add,
                    '-': subtract,
                    '*': multiply,
                    '/': divide
                }
            
            def calculate(self, a: float, operator: str, b: float) -> float:
                """Perform calculation based on operator."""
                if operator not in self.operations:
                    raise ValueError(f"Unknown operator: {operator}")
                
                return self.operations[operator](a, b)
            
            def store_in_memory(self, value: float) -> None:
                """Store a value in memory."""
                self.memory = value
            
            def recall_memory(self) -> float:
                """Recall value from memory."""
                return self.memory
            
            def clear_memory(self) -> None:
                """Clear the memory."""
                self.memory = 0
    "#
  }
}
