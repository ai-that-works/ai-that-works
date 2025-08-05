# Fix @assert vs @@assert Syntax Validation in BAML Tests

## Overview

This plan addresses a critical validation gap where `@assert` (single @) is incorrectly accepted in test blocks by the linter/LSP but is silently ignored at runtime. Only `@@assert` (double @@) actually evaluates assertions, leading to false-positive test results.

## Current State Analysis

### How It Currently Works:
1. **Grammar Level**: BAML distinguishes between:
   - `@attribute` - Field-level attributes for type fields
   - `@@attribute` - Block-level attributes for classes, enums, and test blocks

2. **Test Parsing**:
   - Test blocks are parsed as "value expression blocks"
   - Only test blocks are allowed to have block-level attributes (@@assert, @@check)
   - Field-level attributes (@assert) on test fields are parsed but never validated

3. **Constraint Collection**:
   - `visit_test_case` in `configurations.rs` only collects block-level attributes as constraints
   - Field-level attributes are completely ignored
   - Only collected constraints are passed to runtime evaluation

### Key Discoveries:
- **Parser Location**: `engine/baml-lib/parser-database/src/walkers/parse_value_expression_block.rs:106-125` - validates block attributes
- **Validation Gap**: `engine/baml-lib/parser-database/src/types/configurations.rs:203-300` - `visit_test_case` doesn't validate field attributes
- **Runtime Evaluation**: `engine/baml-lib/baml-core/src/evaluate/test_constraints.rs` - only evaluates collected constraints

## What We're NOT Doing

- Changing the grammar or parser rules
- Modifying runtime constraint evaluation logic
- Altering how @@assert works (it's already correct)
- Changing attribute syntax for non-test contexts
- Modifying test execution behavior

## Implementation Approach

Add validation in the `visit_test_case` function to detect and reject field-level constraint attributes (@assert, @check) within test blocks, providing clear error messages that guide users to use block-level syntax (@@assert, @@check).

## Phase 1: Add Field Attribute Validation in Test Blocks

### Overview
Modify the `visit_test_case` function to validate that fields within test blocks don't have invalid attributes like @assert or @check.

### Changes Required:

#### 1. Update Test Case Validation
**File**: `engine/baml-lib/parser-database/src/types/configurations.rs`
**Changes**: Add validation after processing fields (around line 263)

```rust
// After the fields loop (around line 263)
// Add validation for field-level attributes that shouldn't be in test blocks
for field in &config.fields {
    // Check if the field has any attributes
    if let Some(expr) = &field.expr {
        for attribute in &expr.attributes {
            let attr_name = &attribute.name.name;

            // Check for constraint attributes that should be block-level
            if matches!(attr_name.as_str(), "assert" | "check") {
                ctx.push_error(DatamodelError::new_attribute_validation_error(
                    &format!(
                        "The '@{}' attribute is not allowed on fields within test blocks. Use '@@{}' at the block level instead.",
                        attr_name, attr_name
                    ),
                    &attribute.name.name,
                    attribute.span.clone(),
                ));
            }

            // Also check for other field-only attributes that don't make sense in tests
            if matches!(attr_name.as_str(), "description" | "alias" | "skip") {
                ctx.push_error(DatamodelError::new_attribute_not_known_error(
                    &attribute.name.name,
                    attribute.span.clone(),
                ));
            }
        }
    }
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Existing tests pass: `cd ../../baml && cargo test`
- [ ] Type checking passes: `cd ../../baml && cargo check`
- [ ] Linting passes: `cd ../../baml && cargo clippy`

#### Manual Verification:
- [ ] VSCode shows errors when using @assert in test blocks
- [ ] Error message clearly suggests using @@assert instead
- [ ] Existing valid @@assert tests continue to work
- [ ] Parser correctly rejects @assert but accepts @@assert

---

## Phase 2: Add Comprehensive Test Coverage

### Overview
Add test cases to ensure the validation works correctly and prevents regressions.

### Changes Required:

#### 1. Add Validation Tests
**File**: Create new test file or add to existing parser validation tests
**Changes**: Add test cases for the new validation

```rust
#[test]
fn test_reject_field_level_assert_in_test_blocks() {
    let input = r#"
        test SimpleTest {
            functions [Simple]
            args {
                input "test"
            }
            @assert(this == "Hello, foo!")  // This should error
        }
    "#;

    let result = parse_schema(input);
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("not allowed on fields within test blocks"));
}

#[test]
fn test_accept_block_level_assert_in_test_blocks() {
    let input = r#"
        test SimpleTest {
            functions [Simple]
            args {
                input "test"
            }
            @@assert(this == "Hello, foo!")  // This should work
        }
    "#;

    let result = parse_schema(input);
    assert!(result.is_ok());
}

#[test]
fn test_multiple_invalid_attributes_in_test() {
    let input = r#"
        test ComplexTest {
            functions [Complex]
            args {
                data {
                    field1 "value1" @description("not allowed")
                    field2 "value2"
                }
            }
            @check(data.field1 == "value1")  // Should error
            @assert(data.field2 == "value2") // Should error
        }
    "#;

    let result = parse_schema(input);
    assert!(result.is_err());
    let errors = result.unwrap_err();
    assert_eq!(errors.len(), 3); // One for @description, two for constraints
}
```

### Success Criteria:

#### Automated Verification:
- [ ] New tests pass: `cd ../../baml && cargo test`
- [ ] Test coverage includes all edge cases
- [ ] Error messages are helpful and actionable

#### Manual Verification:
- [ ] Tests demonstrate the fix prevents the original bug
- [ ] Edge cases are covered (multiple attributes, nested fields, etc.)

---

## Phase 3: Update Documentation and Error Messages

### Overview
Ensure error messages are clear and help users understand the correct syntax.

### Changes Required:

#### 1. Enhanced Error Messages
**File**: `engine/baml-lib/parser-database/src/types/configurations.rs`
**Changes**: Refine error messages to be more helpful

```rust
// Provide different messages based on context
let error_msg = match attr_name.as_str() {
    "assert" => format!(
        "Test assertions must use block-level syntax '@@assert' instead of '@assert'. \
         Example:\n  test MyTest {{\n    functions [MyFunc]\n    args {{}}\n    \
         @@assert(this == \"expected\")\n  }}"
    ),
    "check" => format!(
        "Test checks must use block-level syntax '@@check' instead of '@check'. \
         Block-level attributes apply to the entire test result."
    ),
    _ => format!(
        "The '@{}' attribute is not allowed on fields within test blocks.",
        attr_name
    ),
};

ctx.push_error(DatamodelError::new_attribute_validation_error(
    &error_msg,
    &attribute.name.name,
    attribute.span.clone(),
));
```

### Success Criteria:

#### Automated Verification:
- [ ] Error messages include examples of correct syntax
- [ ] All tests still pass with updated messages

#### Manual Verification:
- [ ] Error messages are clear and actionable
- [ ] Users can easily fix their syntax based on the error
- [ ] VSCode displays the full error message with formatting

---

## Testing Strategy

### Unit Tests:
- Test rejection of @assert in test blocks
- Test acceptance of @@assert in test blocks
- Test other invalid field attributes in test contexts
- Test nested field attributes are caught
- Test error message content and clarity

### Integration Tests:
- Verify LSP shows errors in VSCode for invalid syntax
- Ensure existing valid tests continue to work
- Test that runtime behavior is unchanged for valid @@assert

### Manual Testing Steps:
1. Create a BAML file with @assert in a test block
2. Verify VSCode shows a red squiggly with helpful error
3. Change @assert to @@assert and verify error disappears
4. Run the test and verify @@assert actually evaluates
5. Try various invalid attributes (@check, @description, etc.)

## Performance Considerations

The validation adds a loop through test fields and their attributes, but:
- Only runs during parsing/validation phase
- Number of fields in test blocks is typically small
- No impact on runtime performance
- Negligible impact on IDE responsiveness

## Migration Notes

This is a backward-compatible change that only adds validation:
- Existing valid @@assert tests continue to work
- Invalid @assert tests that were silently failing will now show errors
- No migration needed for correct code
- Users with incorrect @assert will see clear errors guiding them to fix

## References

- Grammar definition: `engine/baml-lib/parser-database/src/parser_impl/baml_parser_impl/datamodel.pest`
- Test parsing: `engine/baml-lib/parser-database/src/walkers/parse_value_expression_block.rs`
- Validation location: `engine/baml-lib/parser-database/src/types/configurations.rs:203-300`
- Runtime evaluation: `engine/baml-lib/baml-core/src/evaluate/test_constraints.rs`
- Error patterns: `engine/baml-lib/diagnostics/src/error.rs`
