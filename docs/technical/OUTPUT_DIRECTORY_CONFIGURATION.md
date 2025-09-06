# CodeSentinel Output Directory Configuration

## 🎯 Overview

This document outlines the changes made to ensure CodeSentinel works correctly with the new directory structure after the restructuring completed on September 7, 2025.

## 📁 New Directory Structure Support

### Configuration Updates

**File: `config.yaml`**
- Added `output` section with configurable directory paths
- Default analysis results go to current directory (root)
- Test data goes to `tests/data/` 
- Configurable default filenames for manifest and token analysis

```yaml
output:
  default_dir: "analysis-results"         # Main analyses in dedicated folder
  test_data_dir: "tests/data"             # Test files in tests/data
  manifest: "manifest.json"               # Default manifest filename
  token_analysis: "token_analysis.json"   # Default token analysis filename
```

## 🔧 Code Changes Made

### 1. CLI Updates (`cli.py`)

**Changes:**
- `analyze` command: Now uses config defaults when `--output` not specified
- `analyze-tokens` command: Now uses config defaults when `--output` not specified  
- Both commands automatically create output directories if needed

**Behavior:**
- User-specified paths: Used exactly as provided
- No path specified: Uses config defaults (root directory for main analyses)
- Maintains backward compatibility

### 2. Source Code Updates

**`src/github_analyzer.py`:**
- Main function now saves test files to `tests/data/` directory
- Creates directory automatically if it doesn't exist

**`src/token_analyzer.py`:**
- Main function looks for input files in `tests/data/` first, then root
- Saves output to configured default directory
- Uses config-specified filenames

### 3. Example Scripts (`examples/`)

**`examples/quick_openai_demo.py`:**
- Now saves output to `tests/data/codesentinel_openai_analysis.json`
- Creates `tests/data/` directory automatically

### 4. Test Files (`tests/`)

**`tests/test_phase1.py`:**
- Saves test manifest to `tests/data/test_manifest_phase1.json`
- Creates directory automatically if needed

### 5. Utilities (`cost_estimator.py`)

**`cost_estimator.py`:**
- Saves React analysis to `tests/data/react_cost_analysis.json`
- Creates directory automatically

## 🚦 File Path Resolution Logic

### For Main Analysis Commands

1. **User specifies `--output path`**: Use exactly as specified
2. **No `--output` specified**: Use `config.output.default_dir + config.output.manifest`
3. **Default**: Analysis results directory (`./analysis-results/manifest.json`)

### For Test/Demo Scripts

1. **Check `tests/data/` first** for input files
2. **Fallback to root** if not found in tests/data
3. **Save output to `tests/data/`** for all test/demo scripts

### For Token Analysis

1. **User specifies `--output path`**: Use exactly as specified  
2. **No `--output` specified**: Use `config.output.default_dir + config.output.token_analysis`
3. **Default**: Analysis results directory (`./analysis-results/token_analysis.json`)

## ✅ Verification Commands

Test that the new structure works:

```bash
# Test basic analysis (should save to root)
python cli.py analyze --phase 1 https://github.com/octocat/Hello-World

# Test with custom output (should save where specified)  
python cli.py analyze --phase 1 --output tests/data/my_test.json https://github.com/octocat/Hello-World

# Test token analysis (should save to root by default)
python cli.py analyze-tokens tests/data/manifest.json

# Test examples (should save to tests/data/)
python examples/quick_openai_demo.py
```

## 🎁 Benefits

1. **Backward Compatible**: Existing commands work the same way
2. **Configurable**: Users can change default paths via config
3. **Organized**: Test data automatically goes to appropriate directories
4. **Flexible**: Users can override paths when needed
5. **Auto-Creation**: Directories created automatically when needed

## 📝 Migration Notes

### For Existing Users

- **No breaking changes**: All existing commands work the same
- **Default behavior unchanged**: Main analyses still save to current directory
- **Optional configuration**: Can set custom defaults in `config.yaml`

### For Developers

- **Test files**: Now automatically organized in `tests/data/`
- **Examples**: Output saved to appropriate test directory
- **Config-driven**: Easy to change default paths for different environments

## 🔮 Future Enhancements

Consider adding:

1. **Environment-specific configs**: Dev vs. production output paths
2. **Timestamped directories**: Automatic date-based organization
3. **Project-based organization**: Group outputs by analyzed repository
4. **Cleanup utilities**: Scripts to manage old analysis files

---

**Status**: ✅ Complete - All files updated and tested  
**Date**: September 7, 2025  
**Version**: Post-restructuring compatibility update
