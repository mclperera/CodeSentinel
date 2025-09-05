# CodeSentinel - GitHub Repository Risk Analysis

CodeSentinel is an automated workflow that analyzes GitHub repositories to identify code purpose, assess vulnerabilities, and generate risk scores using GitHub APIs, AWS Bedrock LLM, and CodeQL vulnerability data.

## Phase 1: GitHub Integration & Manifest Generation ✅

Phase 1 provides core GitHub repository analysis capabilities including repository discovery, branch detection, blob extraction, and initial manifest generation.

### Features

- **Repository Discovery**: Automatically identify default branch and retrieve repository metadata
- **Code Extraction**: Use Git Trees API to traverse repository structure and extract file contents
- **File Inventory**: Generate comprehensive file inventory with metadata
- **Manifest Generation**: Create structured JSON manifest with file information
- **CLI Interface**: Command-line tools for repository analysis

### Prerequisites

- Python 3.9+
- GitHub Personal Access Token with repository read permissions
- Internet connection for GitHub API access

### Installation

1. Clone or download the CodeSentinel repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your GitHub token in the `.env` file:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

### Usage

#### Command Line Interface

```bash
# Analyze a repository and generate manifest
python cli.py analyze https://github.com/owner/repo

# Analyze with custom output file
python cli.py analyze https://github.com/owner/repo --output my_manifest.json

# Test GitHub connection
python cli.py test-connection

# Display manifest information
python cli.py show manifest.json

# Get specific file content
python cli.py get-file https://github.com/owner/repo path/to/file.py
```

#### Python API

```python
from src.github_analyzer import GitHubAnalyzer

# Initialize analyzer
analyzer = GitHubAnalyzer()

# Generate manifest for a repository
manifest = analyzer.generate_manifest("https://github.com/owner/repo")

# Save manifest to file
analyzer.save_manifest(manifest, "manifest.json")

# Load existing manifest
loaded_manifest = analyzer.load_manifest("manifest.json")
```

### Configuration

The `config.yaml` file allows customization of analysis parameters:

```yaml
analysis:
  file_extensions: [".py", ".js", ".java", ".go", ".rb", ".php", ".ts", ".jsx", ".tsx"]
  max_file_size: 1048576  # 1MB
  batch_size: 10
```

### Manifest Structure

The generated manifest follows this JSON structure:

```json
{
  "repository": {
    "url": "https://github.com/owner/repo",
    "default_branch": "main",
    "commit_sha": "abc123...",
    "analysis_timestamp": "2025-09-05T..."
  },
  "files": [
    {
      "path": "src/main.py",
      "blob_sha": "def456...",
      "size": 2048,
      "extension": ".py",
      "purpose": null,
      "confidence_score": null,
      "vulnerabilities": [],
      "risk_score": null
    }
  ]
}
```

### Testing

Run the test script to verify Phase 1 functionality:

```bash
python test_phase1.py
```

This will:
- Test GitHub API connection
- Analyze a sample repository
- Generate and save a manifest
- Verify manifest loading
- Test CLI interface

### Supported File Types

Phase 1 analyzes the following file types by default:
- Python (`.py`)
- JavaScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Java (`.java`)
- Go (`.go`)
- Ruby (`.rb`)
- PHP (`.php`)
- C/C++ (`.c`, `.cpp`, `.h`)
- C# (`.cs`)
- SQL (`.sql`)
- Configuration files (`.yaml`, `.yml`, `.json`, `.xml`)
- Web files (`.html`, `.css`)

### Error Handling

- **Rate Limiting**: Automatic handling of GitHub API rate limits with exponential backoff
- **Large Files**: Files exceeding the size limit (default 1MB) are skipped
- **Network Issues**: Robust error handling and retry logic
- **Invalid Repositories**: Clear error messages for inaccessible or invalid repositories

### GitHub API Permissions

Your GitHub token needs the following permissions:
- `public_repo` (for public repositories)
- `repo` (for private repositories you have access to)

### Next Phase

Phase 1 provides the foundation for:
- **Phase 2**: LLM-powered code analysis using AWS Bedrock
- **Phase 3**: Vulnerability integration with CodeQL
- **Phase 4**: Risk scoring algorithm implementation

## Directory Structure

```
CodeSentinel/
├── src/
│   └── github_analyzer.py      # Core GitHub integration module
├── cli.py                      # Command-line interface
├── test_phase1.py             # Test script for Phase 1
├── config.yaml                # Configuration file
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (GitHub token)
├── github_analysis_prd.md     # Product Requirements Document
└── README.md                  # This file
```

## License

This project is part of the CodeSentinel risk analysis workflow implementation.

## Support

For issues or questions about Phase 1 implementation, please refer to the PRD document or check the error logs generated during analysis.
