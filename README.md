# CodeSentinel

🛡️ **Automated GitHub repository risk analysis using AI-powered insights**

CodeSentinel is an intelligent repository analysis tool that combines GitHub API integration with AWS Bedrock LLM capabilities to provide comprehensive code understanding and risk assessment.

## Quick Start

```bash
git clone https://github.com/mclperera/CodeSentinel
cd CodeSentinel
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure your GitHub token and AWS credentials
echo "your_github_token_here" > .env

# Analyze a repository
python cli.py analyze --phase 3 --provider openai https://github.com/owner/repo
```

## Documentation

📚 **[Complete Documentation](docs/README.md)** - Detailed guides, architecture, and examples

### Quick Links
- [Design Documents](docs/design/) - PRD and architecture decisions
- [Phase Development](docs/phase-summaries/) - Development progress and milestones  
- [Analysis Results](docs/analysis-results/) - Research findings and cost analysis
- [Technical Guides](docs/technical/) - Implementation details and explanations
- [Examples](examples/) - Demo scripts and usage examples

## Project Structure

```
CodeSentinel/
├── src/              # Core source code
├── docs/             # Complete documentation
├── tests/            # Tests and test data
├── examples/         # Demo scripts
├── analysis-results/ # Generated analysis outputs
├── cli.py           # Command-line interface
└── config.yaml      # Configuration

### Usage

#### Basic Repository Analysis (Phase 1)
```bash
python cli.py analyze https://github.com/owner/repo --phase 1
```

#### AI-Enhanced Analysis (Phase 2.5)
```bash
python cli.py analyze https://github.com/owner/repo --phase 2.5 --provider openai
```

#### Vulnerability Scanning (Phase 3)
```bash
python cli.py analyze https://github.com/owner/repo --phase 3
```

#### Combined Analysis with Vulnerability Scanning
```bash
python cli.py analyze https://github.com/owner/repo --phase 2.5 --scan-vulnerabilities
```

#### View Analysis Results
```bash
python cli.py show manifest.json
```

#### Test Connections
```bash
python cli.py test-connection              # GitHub API
python cli.py test-llm                     # LLM providers  
python cli.py test-vulnerability-scanner   # Security tools
```

## 📊 Supported File Types

- **Programming Languages**: Python, JavaScript, TypeScript, Java, Go, Ruby, PHP, C/C++, C#
- **Web Technologies**: HTML, CSS, JSX, TSX
- **Configuration**: YAML, JSON, XML
- **Database**: SQL
- **Documentation**: Various formats

## 🔧 Configuration

### config.yaml
```yaml
github:
  token: "${GITHUB_TOKEN}"
  api_base_url: "https://api.github.com"
  
aws:
  region: "us-east-1"
  bedrock_model: "anthropic.claude-3-5-sonnet-20240620-v1:0"
  
analysis:
  file_extensions: [".py", ".js", ".java", ".go", ".rb", ".php", ...]
  max_file_size: 1048576  # 1MB
  batch_size: 10
  
risk_scoring:
  weights:
    vulnerability: 0.4
    purpose: 0.3
    exposure: 0.2
    complexity: 0.1

# Phase 3: Vulnerability scanning
vulnerability_scanning:
  semgrep:
    enabled: true
    timeout: 120
  bandit:
    enabled: true
    confidence_level: "low"
```

## 📋 Manifest Structure

### Phase 1 Output
```json
{
  "repository": {
    "url": "https://github.com/owner/repo",
    "default_branch": "main",
    "commit_sha": "abc123...",
    "analysis_timestamp": "2025-09-06T..."
  },
  "files": [
    {
      "path": "src/app.py",
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

### Phase 2 Enhanced Output
```json
{
  "files": [
    {
      "path": "src/auth/login.py",
      "purpose": "User authentication and session management",
      "confidence_score": 0.95,
      "llm_metadata": {
        "category": "authentication",
        "security_relevance": "high",
        "reasoning": "Handles credentials and access control"
      }
    }
  ]
}
```

## 🛠️ CLI Commands

### Analysis Commands
- `analyze <repo_url>` - Analyze repository (specify `--phase 1` or `--phase 2`)
- `show <manifest_path>` - Display manifest information
- `get-file <repo_url> <file_path>` - Extract specific file content

### Testing Commands
- `test-connection` - Validate GitHub API access
- `test-llm` - Validate AWS Bedrock connectivity

### Options
- `--output, -o` - Specify output file path
- `--config, -c` - Use custom configuration file
- `--phase, -p` - Select analysis phase (1 or 2)
- `--aws-profile` - Specify AWS profile for Bedrock

## 📈 Performance Metrics

### Tested Repositories
- **CPython**: 3,435 files analyzed successfully
- **Requests Library**: 50 files with full LLM analysis
- **Flask Framework**: 116 files processed in Phase 1

### Analysis Speed
- **Phase 1**: ~1000 files per minute (metadata extraction)
- **Phase 2**: ~10-50 files per minute (LLM analysis, rate-limited)

## 🔒 Security Features

- **Secure Token Management**: Environment variable storage
- **Rate Limiting Protection**: Exponential backoff for API calls
- **Error Handling**: Graceful degradation and retry logic
- **Access Control**: IAM-based AWS authentication

## 🏗️ Architecture

```
CodeSentinel/
├── src/
│   ├── github_analyzer.py    # GitHub API integration
│   ├── llm_analyzer.py       # AWS Bedrock LLM integration
│   └── test_bedrock.py       # Connectivity testing
├── cli.py                    # Command-line interface
├── config.yaml              # Configuration management
├── requirements.txt          # Python dependencies
├── PHASE1_SUMMARY.md        # Phase 1 documentation
├── PHASE2_SUMMARY.md        # Phase 2 documentation
└── github_analysis_prd.md   # Product requirements
```

## 📊 Analysis Categories

The LLM analyzer classifies files into the following categories:

- **Authentication**: Login, session management, access control
- **Data Processing**: ETL, data transformation, analysis
- **API**: REST endpoints, GraphQL, service interfaces
- **Frontend**: UI components, client-side logic
- **Configuration**: Settings, environment, deployment
- **Test**: Unit tests, integration tests, test utilities
- **Build**: CI/CD, packaging, deployment scripts
- **Documentation**: README, docs, comments
- **Other**: Miscellaneous files not fitting above categories

## 🔮 Roadmap

### ✅ Phase 3: Vulnerability Integration (Complete)
- [x] Semgrep integration for comprehensive security scanning
- [x] Bandit integration for Python security analysis  
- [x] Automatic tool installation and management
- [x] Repository cloning and local analysis
- [x] Vulnerability-to-file mapping with detailed findings
- [x] CLI integration with --scan-vulnerabilities flag

### Phase 4: Risk Assessment (Planned)
- [ ] Weighted risk calculation using vulnerability data
- [ ] Repository-level risk scoring algorithm
- [ ] Risk categorization and reporting dashboard
- [ ] Integration with LLM insights for context-aware scoring
- [ ] Compliance reporting features

### Future Enhancements
- [ ] Additional security tools (CodeQL, Safety, etc.)
- [ ] VS Code extension with real-time scanning
- [ ] Web dashboard for vulnerability management
- [ ] Batch repository processing for organizations
- [ ] Custom risk weight configuration
- [ ] Integration with security orchestration platforms

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: See phase-summaries/ for detailed development progress
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Requirements**: See github_analysis_prd.md for detailed specifications

## 🏆 Achievements

✅ **Phase 1 Complete**: GitHub integration and manifest generation  
✅ **Phase 2.5 Complete**: Multi-provider LLM analysis (OpenAI + AWS Bedrock)  
✅ **Phase 3 Complete**: Vulnerability scanning (Semgrep + Bandit)  
📋 **Phase 4 Planned**: Risk scoring and assessment algorithms

---

**Built with ❤️ using Python, GitHub APIs, LLM providers, and security tools**

CodeSentinel is an automated workflow that analyzes GitHub repositories to identify code purpose, assess vulnerabilities, and generate risk scores using GitHub APIs, AI-powered analysis, and comprehensive security scanning.

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
