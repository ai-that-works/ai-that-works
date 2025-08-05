## History

Documentation of the prep process

### Step 1 - a bad research

CONTEXT WINDOW 1

the file at thoughts/shared/research/

was produced badly, it decided, among other things, that there was no bug and that the issue should be closed.

### Step 2 - refining the spec

I updated the spec with more detail about what's not working

https://github.com/BoundaryML/baml/issues/1252#issuecomment-3153241089


### Step 3 - resteering the research

I pasted the updated comment into the CONTEXT WINDOW 1, and asked for an improved research prompt, that would help us track down the issues location more closely.

it gave us back

<details><summary>improved research prompt</summary>

```
  Research BAML Test Assertion Linter Bug - Issue #1252

  Context

  Issue #1252 reports that BAML tests incorrectly accept @assert (single @) syntax without any
  linter warnings, but these assertions are silently ignored at runtime. Only @@assert (double
  @) assertions are actually evaluated during test execution.

  The Problem

  1. Linter / LSP accepts invalid syntax: @assert in test blocks passes linting without errors - we expect vscode errors when single-@ assert is used
  2. Silent failure: Tests with @assert run successfully even when assertions should fail
  3. Only @@assert works: Double @@ is the correct syntax that actually evaluates assertions

  Example Test Cases

  Broken (passes when it shouldn't):

  test SimpleTest {
    functions [Simple]
    args {}
    @assert(Simple, {{this == "Hello, foo!"}})  # WRONG: Single @ - silently ignored
  }

  Working correctly:

  test SimpleTest {
    functions [Simple]
    args {}
    @@assert(Simple, {{this == "Hello, foo!"}})  # CORRECT: Double @@ - properly evaluated
  }

  Research Goals

  1. Find where test assertions are parsed - Why does the parser accept @assert in test blocks?
  2. Locate the linter validation gap - Where should validation reject single @ in tests?
  3. Understand assertion evaluation - Why are @assert assertions ignored at runtime?
  4. Identify the fix location - Where to add validation to reject @assert in test blocks?

  Key Areas to Investigate

  - Test block parsing and validation logic
  - Assertion attribute handling in test contexts
  - Difference between field attributes (@) and block attributes (@@) in tests
  - Runtime assertion evaluation that ignores single @ assertions

  Expected Outcome

  Find the exact location where the linter should be modified to:
  1. Reject @assert syntax in test blocks with a clear error message
  2. Only allow @@assert and @@check in test contexts
  3. Prevent silent failures from incorrectly formatted assertions

  The fix should be a "good first issue" - likely adding validation logic to catch single @
  usage in test blocks during the linting phase.

```

</details>

### Step 4 - research attempt 2

Created a fresh CONTEXT WINDOW 2, and ran `/research_codebase`, pasting in the response from above!

It failed, it fixated on the previous bad research, and told us we were wrong

at this point I realized I was on a baml branch that handn't been updated in 6+ months, so I threw both research docs out

### Step 4 - research attempt 3

Same fancy prompt from above, fresh CONTEXT WINDOW 3, and a fresh baml checkout off their default `canary` branch.

### Step 5 - plan attempt with no research

I was getting impatient and wondered if we could spin up a plan without any research, and see if that would work. Start CONTEXT WINDOW 4 - with the same DETAILED prompt from step 3

### Step 6 - plan attempt with research
