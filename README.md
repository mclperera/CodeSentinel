# CodeSentinel

🛡️ **Automated GitHub repository risk analysis using AI-powered insights**

CodeSentinel is an intelligent repository analysis tool that combines GitHub API integration with LLM capabilities to provide comprehensive code understanding and **intelligent vulnerability risk assessment**.

> ⚠️ **Educational Project**: This tool is designed for educational purposes and learning. It uses paid APIs (OpenAI, AWS Bedrock) and should be used responsibly. Always review cost estimates before analyzing large repositories. See [Security Policy](SECURITY.md) for important considerations.

## ✨ Features

- 🔍 **Multi-phase Repository Analysis** - Progressive enhancement from structure to AI insights to vulnerabilities
- 🧠 **LLM-Powered File Understanding** - AI categorization and security relevance assessment  
- 🛡️ **Comprehensive Vulnerability Scanning** - Semgrep + Bandit integration with intelligent filtering
- 🎯 **Smart Risk Scoring** - Configurable risk assessment combining vulnerability severity, file purpose, and business context
- ⚙️ **Fully Configurable** - User-customizable risk scoring rules and priority thresholds
- 📊 **Actionable Prioritization** - CRITICAL/HIGH/MEDIUM/LOW priorities with clear SLAs

## Quick Start

```bash
git clone https://github.com/mclperera/CodeSentinel
cd CodeSentinel
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure your tokens
echo "GITHUB_TOKEN=your_github_token_here" > .env
echo "OPENAPI_KEY=your_openai_key_here" >> .env

# Sequential analysis workflow (recommended)
python cli.py analyze https://github.com/owner/repo --phase 1      # Basic structure
python cli.py analyze https://github.com/owner/repo --phase 2.5    # Add AI insights  
python cli.py analyze https://github.com/owner/repo --phase 3      # Add vulnerabilities + risk scores
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

#### Sequential Analysis Workflow (Recommended)

CodeSentinel uses **progressive enhancement** - each phase builds upon previous data in the same file:

**Step 1: Basic Repository Structure**
```bash
python cli.py analyze https://github.com/owner/repo --phase 1
```

**Step 2: AI-Enhanced Analysis (adds purpose and insights)**
```bash
python cli.py analyze https://github.com/owner/repo --phase 2.5 --provider openai
```

**Step 3: Vulnerability Scanning (adds security findings)**
```bash
python cli.py analyze https://github.com/owner/repo --phase 3
```

#### Custom Output File (Sequential Enhancement)
```bash
# Use custom filename - each phase enhances the SAME file
python cli.py analyze https://github.com/pallets/flask --phase 1 --output flask-analysis.json
python cli.py analyze https://github.com/pallets/flask --phase 2.5 --output flask-analysis.json  
python cli.py analyze https://github.com/pallets/flask --phase 3 --output flask-analysis.json
# Result: Single comprehensive file with structure + AI insights + vulnerabilities
```

#### Combined Analysis
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

### Risk Scoring Configuration (risk_scoring_config.yaml)
```yaml
# Configurable risk scoring weights and thresholds
risk_component_weights:
  vulnerability_severity: 0.40  # 40% weight for vulnerability severity
  file_category: 0.35          # 35% weight for file category
  security_relevance: 0.25     # 25% weight for security relevance

# Vulnerability severity scoring (0-10)
vulnerability_severity_scores:
  critical: 10.0
  high: 7.0
  medium: 5.0
  low: 3.0
  info: 1.0

# File category scoring (0-10)  
file_category_scores:
  authentication: 9.0
  api: 8.0
  data-processing: 7.0
  config: 6.0
  frontend: 4.0
  build: 3.0
  test: 2.0
  documentation: 1.0
  other: 2.0

# Priority thresholds and SLA hours
priority_thresholds:
  CRITICAL: {min: 8.0, sla_hours: 4}
  HIGH: {min: 6.0, sla_hours: 24}
  MEDIUM: {min: 4.0, sla_hours: 72}
  LOW: {min: 2.0, sla_hours: 168}
  INFO: {min: 0.0, sla_hours: 720}
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

### Phase 3 Vulnerability-Enhanced Output
```json
{
  "files": [
    {
      "path": "src/auth/login.py",
      "purpose": "User authentication and session management",
      "vulnerabilities": [
        {
          "scanner": "semgrep",
          "rule_id": "python.flask.security.hardcoded-secret",
          "severity": "high",
          "message": "Hardcoded secret detected"
        }
      ],
      "risk_assessment": {
        "risk_score": 8.4,
        "priority": "CRITICAL",
        "sla_hours": 4,
        "components": {
          "vulnerability_severity": 7.0,
          "file_category": 9.0,
          "security_relevance": 9.0
        }
      }
    }
  ]
}
```

## 🛠️ CLI Commands

### Analysis Commands
- `analyze <repo_url>` - Analyze repository (specify `--phase 1` or `--phase 2`)
- `analyze <repo_url> --scan-vulnerabilities` - Full analysis with vulnerability scanning and risk scoring
- `show <manifest_path>` - Display manifest information
- `get-file <repo_url> <file_path>` - Extract specific file content

### Testing Commands
- `test-connection` - Validate GitHub API access
- `test-llm` - Validate AWS Bedrock connectivity
- `test-vulnerability-scanner` - Test Semgrep and Bandit installation

### Options
- `--output, -o` - Specify output file path
- `--config, -c` - Use custom configuration file
- `--phase, -p` - Select analysis phase (1 or 2)
- `--scan-vulnerabilities` - Enable Phase 3 vulnerability scanning with risk assessment
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
│   ├── github_analyzer.py       # GitHub API integration
│   ├── llm_analyzer.py          # AWS Bedrock LLM integration
│   ├── multi_llm_analyzer.py    # Multi-provider LLM support
│   ├── vulnerability_scanner.py # Semgrep & Bandit integration
│   ├── risk_scorer.py          # Configurable risk assessment engine
│   └── test_bedrock.py          # Connectivity testing
├── prompts/
│   ├── analysis_prompts.py      # LLM prompt templates
│   ├── system_prompts.py        # System-level prompts
│   └── prompt_utils.py          # Prompt utilities
├── cli.py                       # Command-line interface
├── config.yaml                  # Main configuration
├── risk_scoring_config.yaml     # Risk scoring configuration
├── requirements.txt             # Python dependencies
└── docs/                        # Documentation and guides
    ├── risk-scoring.md          # Risk scoring documentation
    └── phase-summaries/         # Development phase docs
```

## 🎯 Smart Risk Scoring System

CodeSentinel features a fully configurable risk scoring system that automatically prioritizes vulnerabilities based on multiple factors. The system combines vulnerability severity with file categorization and security relevance to generate actionable risk assessments.

### Risk Calculation Method

The risk scoring engine uses a **3-factor weighted approach**:

- **Vulnerability Severity (40%)**: Based on scanner findings (Critical, High, Medium, Low, Info)
- **File Category (35%)**: Authentication files get higher scores than documentation
- **Security Relevance (25%)**: LLM-determined security importance

### Priority Classification

Files are automatically classified into 5 priority levels:

| Priority | Risk Score | SLA Response | Example Files |
|----------|------------|--------------|---------------|
| 🔴 **CRITICAL** | 8.0+ | 4 hours | Authentication with high severity vulns |
| 🟠 **HIGH** | 6.0-8.0 | 24 hours | API endpoints with medium severity vulns |
| 🟡 **MEDIUM** | 4.0-6.0 | 72 hours | Configuration files with low severity vulns |
| 🔵 **LOW** | 2.0-4.0 | 168 hours | Frontend with info-level findings |
| ⚪ **INFO** | 0.0-2.0 | 720 hours | Documentation with minimal issues |

### Configurable Scoring

All scoring parameters are user-configurable via `risk_scoring_config.yaml`:

```yaml
# Customize component weights
risk_component_weights:
  vulnerability_severity: 0.40  # Adjust vulnerability importance
  file_category: 0.35          # Adjust file type importance
  security_relevance: 0.25     # Adjust LLM assessment importance

# Customize file category scores
file_category_scores:
  authentication: 9.0  # Critical security files
  api: 8.0            # External interfaces
  config: 6.0         # Configuration files
  test: 2.0           # Test files
  # ... customize all categories

# Customize priority thresholds and SLA times
priority_thresholds:
  CRITICAL: {min: 8.0, sla_hours: 4}
  HIGH: {min: 6.0, sla_hours: 24}
  # ... adjust thresholds as needed
```

### Usage Examples

**Analyze with risk scoring (Phase 3):**
```bash
python cli.py analyze https://github.com/pallets/flask --scan-vulnerabilities
```

**Sample risk assessment output:**
```json
{
  "risk_assessment": {
    "risk_score": 8.4,
    "priority": "CRITICAL",
    "sla_hours": 4,
    "components": {
      "vulnerability_severity": 7.0,  # High severity finding
      "file_category": 9.0,           # Authentication file
      "security_relevance": 9.0       # High security relevance
    }
  }
}
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
- [x] **Smart risk scoring system with configurable parameters**
- [x] **Multi-factor risk assessment (severity + category + relevance)**
- [x] **Priority classification with SLA response times**
- [x] **YAML-based configuration for user customization**

### Phase 4: Advanced Risk Features (Planned)
- [ ] Repository-level risk aggregation and reporting
- [ ] Risk trend analysis and historical comparisons
- [ ] Custom risk weight profiles for different industries
- [ ] Integration with security orchestration platforms
- [ ] Compliance framework mapping (OWASP, NIST, etc.)
- [ ] Risk mitigation recommendations and remediation guidance

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
✅ **Phase 3 Complete**: Vulnerability scanning (Semgrep + Bandit) + **Smart Risk Scoring**  
📋 **Phase 4 Planned**: Advanced risk analytics and enterprise features

### 🎯 Latest: Configurable Risk Scoring System
- **Multi-factor Assessment**: Combines vulnerability severity, file category, and security relevance
- **User Configurable**: All scoring parameters customizable via YAML configuration
- **Priority Classification**: Automatic CRITICAL/HIGH/MEDIUM/LOW/INFO categorization
- **SLA Integration**: Response time recommendations for each priority level
- **Real-world Tested**: Validated with Flask repository analysis (116 files, 11 vulnerable)

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
