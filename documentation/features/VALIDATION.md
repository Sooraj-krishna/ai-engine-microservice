# Code Validation & Safety

Safety is paramount when determining if AI-generated code should be applied. We employ a multi-layer validation strategy.

## Validation Layers

### 1. Safety Validation

This checks for dangerous patterns before code is even considered:

- **No System Commands**: Blocks `exec`, `spawn`, `os.system`.
- **No File Deletion**: Blocks `rm`, `unlink`, `shutil.rmtree`.
- **Protected Files**: Prevents modification of `node_modules`, `.env`, or configuration files.

### 2. Syntax Validation

Ensures the generated code is syntactically valid:

- **JavaScript/TypeScript**: Runs `node --check` to verify syntax.
- **Python**: Uses `ast.parse()` to ensure it compiles.
- **HTML/JSX**: Checks for balanced tags and proper structure.

### 3. Execution Testing (Sandbox)

Before applying a fix, we try to run it in isolation:

- **Unit Tests**: Generates on-the-fly tests to verify the fix works.
- **Side Effects**: Checks for unintended global state changes.

## Rejection Criteria

A fix is immediately rejected if:

- It contains any banned dangerous patterns.
- It fails syntax validation.
- It causes a crash during sandbox execution.
- It attempts to remove significant chunks of existing code without replacement.
