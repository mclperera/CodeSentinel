# Getting Started with CodeSentinel

This guide will help you get up and running with CodeSentinel quickly.

## Prerequisites

- Python 3.9 or higher
- GitHub Personal Access Token
- AWS Account with Bedrock access (for AWS provider) OR OpenAI API key (for OpenAI provider)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mclperera/CodeSentinel
   cd CodeSentinel
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### GitHub Token Setup
Create a `.env` file in the root directory:
```bash
echo "your_github_token_here" > .env
```

### Provider Configuration

#### Option 1: AWS Bedrock (Default)
Configure AWS SSO profile named `bedrock-dev` or update `config.yaml` with your preferred profile.

#### Option 2: OpenAI
Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

## Basic Usage

### 1. Estimate Costs First
Before running analysis, estimate the costs:
```bash
python cost_estimator.py https://github.com/owner/repository
```

### 2. Run Analysis
```bash
# Using OpenAI (recommended for beginners)
python cli.py analyze --phase 2.5 --provider openai --output my_analysis.json https://github.com/owner/repository

# Using AWS Bedrock
python cli.py analyze --phase 2.5 --provider bedrock --output my_analysis.json https://github.com/owner/repository
```

### 3. View Results
```bash
python cli.py show my_analysis.json
```

## Example Workflows

### Small Repository Analysis
```bash
# Quick analysis of a small repo
python cli.py analyze --phase 2.5 --provider openai --output hello_world.json https://github.com/octocat/Hello-World
python cli.py show hello_world.json
```

### Large Repository with Cost Check
```bash
# First check costs
python cost_estimator.py https://github.com/facebook/react

# If costs are acceptable, proceed
python cli.py analyze --phase 2.5 --provider openai --output react_analysis.json https://github.com/facebook/react
```

## Understanding Output

The analysis generates a JSON manifest containing:
- **Repository metadata**: Basic info, file counts, languages
- **File analysis**: Purpose identification, categorization, security relevance
- **Cost information**: Token usage and estimated costs
- **Confidence scores**: Reliability metrics for AI analysis

## Troubleshooting

### Common Issues

1. **GitHub API Rate Limiting**
   - Solution: Wait for rate limit reset or use authenticated requests

2. **AWS Credentials Not Found**
   - Solution: Configure AWS SSO profile or update `config.yaml`

3. **OpenAI API Key Issues**
   - Solution: Verify OPENAI_API_KEY environment variable is set

4. **Large Repository Costs**
   - Solution: Use cost estimator first, consider filtering file types

### Getting Help

- Check [technical documentation](../technical/) for detailed explanations
- Review [examples](../../examples/) for working code samples
- Examine [test data](../../tests/data/) for expected output formats

## Next Steps

- Explore [examples](../../examples/) to understand advanced usage
- Read [phase summaries](../phase-summaries/) to understand development progress
- Check [analysis results](../analysis-results/) for performance benchmarks
