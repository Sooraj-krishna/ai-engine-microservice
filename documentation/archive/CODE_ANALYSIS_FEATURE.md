# Code Analysis Feature

## Overview

The Code Analysis feature provides **better code understanding** by parsing Abstract Syntax Trees (AST) and building dependency graphs. This enables more accurate bug fixes by understanding code structure before making changes.

## What It Does

### 1. **AST Parsing**
- Parses Python files using Python's built-in `ast` module
- Analyzes JavaScript/TypeScript files using regex patterns
- Extracts HTML structure and relationships

### 2. **Dependency Graph Building**
- Maps imports and dependencies between files
- Tracks relationships (which files depend on which)
- Identifies related files for context

### 3. **Code Structure Analysis**
- Extracts functions, classes, and methods
- Maps imports and exports
- Identifies file types and relationships

## How It Works

### Integration Points

1. **Improved Fixer** (`improved_fixer.py`)
   - Automatically analyzes codebase before fixing bugs
   - Provides context about related files and dependencies
   - Helps generate more accurate fixes

2. **Code Analyzer Module** (`code_analyzer.py`)
   - Standalone module for code analysis
   - Can be used independently or integrated with fixers
   - Returns structured analysis data

### Analysis Process

```
1. Repository Scan
   ↓
2. File Type Detection (Python/JS/HTML)
   ↓
3. AST/Pattern Parsing
   ↓
4. Structure Extraction (functions, classes, imports)
   ↓
5. Dependency Graph Building
   ↓
6. Context Generation for Fixes
```

## Features

### Python Analysis
- ✅ Full AST parsing
- ✅ Import extraction
- ✅ Function and class detection
- ✅ Method extraction

### JavaScript/TypeScript Analysis
- ✅ ES6 and CommonJS import detection
- ✅ Function declaration extraction
- ✅ Class and method detection
- ✅ Export identification

### HTML Analysis
- ✅ Script and stylesheet reference tracking
- ✅ ID and class extraction
- ✅ Dependency mapping

### Dependency Graph
- ✅ File-to-file relationships
- ✅ Import/export mapping
- ✅ Related file discovery
- ✅ Context-aware fixing

## Usage

### Automatic Usage
The code analyzer is **automatically used** when:
- Improved Fixer is enabled
- Repository path is available
- Fixing bugs that require code understanding

### Manual Usage
```python
from code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer(repo_path="/path/to/repo")
analysis = analyzer.analyze_repository()

# Get context for a specific file
context = analyzer.get_file_context("src/components/Button.jsx")

# Get related files
related = analyzer.get_related_files("src/components/Button.jsx", max_depth=2)
```

## Impact

### Before Code Analysis
- ❌ Limited context when fixing bugs
- ❌ Risk of breaking dependencies
- ❌ Unaware of related files
- ❌ Generic fixes that might conflict

### After Code Analysis
- ✅ Full codebase understanding
- ✅ Dependency-aware fixes
- ✅ Related file consideration
- ✅ Context-specific accurate fixes

## Status

The code analysis feature is **always enabled** when available. You can see its status in the Status Monitor UI under "Environment" → "Code Analysis".

## Technical Details

### Supported File Types
- Python (`.py`) - Full AST parsing
- JavaScript (`.js`, `.jsx`) - Pattern-based analysis
- TypeScript (`.ts`, `.tsx`) - Pattern-based analysis
- HTML (`.html`, `.htm`) - Structure analysis

### Performance
- Analysis runs once per maintenance cycle
- Results are cached during the cycle
- Minimal performance impact
- Scales to large codebases

### Limitations
- JavaScript/TypeScript uses regex patterns (not full AST)
- Large files may be partially analyzed
- Some complex patterns may not be detected

## Future Improvements

1. **Full JavaScript AST Parsing**
   - Use `esprima` or `acorn` for better JS analysis
   - More accurate dependency detection

2. **Cross-Language Analysis**
   - Understand relationships between Python and JS
   - Track dependencies across language boundaries

3. **Incremental Analysis**
   - Only re-analyze changed files
   - Cache analysis results

4. **Type Inference**
   - Infer types from code
   - Better understanding of data flow

## Configuration

No configuration needed! The code analyzer:
- Automatically detects available files
- Works with any repository structure
- Handles errors gracefully
- Falls back to basic context if analysis fails

## Example

When fixing a bug in `Button.jsx`:

**Without Code Analysis:**
```
Fix: Add aria-label to button
Context: Only the button code itself
```

**With Code Analysis:**
```
Fix: Add aria-label to button
Context:
- File: src/components/Button.jsx
- Imports: React, PropTypes, styles
- Related files: Header.jsx, Footer.jsx (also use Button)
- Dependencies: button.css, button.test.js
- Functions: handleClick, render
```

This context helps generate fixes that:
- Don't break existing imports
- Consider related file usage
- Maintain consistency with dependencies
- Follow existing code patterns

