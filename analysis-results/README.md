# Analysis Results Directory

This directory contains the output files from CodeSentinel repository analyses.

## File Types

- **`manifest.json`** - Default manifest file when no output specified
- **`*_analysis.json`** - Named analysis results (e.g., `flask_analysis.json`)
- **`*_tokens.json`** - Token analysis files (Phase 1.5)
- **`token_analysis.json`** - Default token analysis file

## Organization

Files are automatically saved here when using CLI commands without specifying an output path:

```bash
# These commands save to analysis-results/
python cli.py analyze https://github.com/owner/repo
python cli.py analyze-tokens manifest.json
```

## File Management

- Files in this directory are ignored by Git (see `.gitignore`)
- This keeps generated analysis data separate from source code
- You can safely delete files in this directory - they can be regenerated

## Custom Output Paths

You can still specify custom output locations:

```bash
# Save to a custom location
python cli.py analyze --output /path/to/custom.json https://github.com/owner/repo

# Save to tests/data for testing
python cli.py analyze --output tests/data/test.json https://github.com/owner/repo
```
