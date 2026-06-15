---
name: code-refactor
description: Refactor code for readability, structure, and maintainability without changing external behavior
---

# Code Refactor

Refactor the target code (file, function, or module specified in $ARGUMENTS, or the most recently changed code if no target is given) while preserving its observable behavior.

## Scope

- If $ARGUMENTS names a file, function, or symbol, limit the refactor to that target and its immediate collaborators.
- If $ARGUMENTS is empty, identify the most recently modified or currently selected code and refactor that.
- Do NOT add new features, change public APIs, or alter behavior unless the user explicitly asks.

## Steps

1. **Read the target code** and its callers to understand current behavior and contracts.
2. **Identify refactor opportunities**, prioritized:
   - Duplicated logic that can be extracted
   - Long functions that can be split by responsibility
   - Unclear names (variables, functions, parameters)
   - Dead code or unreachable branches
   - Nested conditionals that can be flattened (early returns, guard clauses)
   - Mixed levels of abstraction within a single function
   - Magic numbers/strings that should be named constants
3. **Check for tests** covering the target. If tests exist, run them before changing anything to establish a baseline. If no tests exist, flag this to the user before proceeding with non-trivial restructuring.
4. **Apply refactors in small, self-contained edits.** Prefer many small mechanical changes over one large rewrite.
5. **Re-run tests after each meaningful change.** If a test fails, stop and investigate — do not continue stacking changes on a broken baseline.
6. **Report a summary** of what changed and why, grouped by refactor type.

## Constraints

- Preserve public function signatures, return types, and side-effect ordering unless the user approves a change.
- Do not introduce new dependencies or abstractions that aren't justified by the code in front of you. Three similar lines is better than a premature abstraction.
- Do not add comments explaining what the code does — rely on good names. Only add a comment when the *why* is non-obvious.
- If the code is already clean, say so and stop. Do not refactor for its own sake.

$ARGUMENTS
