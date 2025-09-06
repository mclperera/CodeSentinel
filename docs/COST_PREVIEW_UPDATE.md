# Cost Preview and User Consent Update - CodeSentinel

## 🎯 Overview

Enhanced CodeSentinel with **tiktoken-based cost estimation** and **user consent** before running expensive LLM analysis operations (Phase 2.5).

## ✨ New Features

### 1. **Cost Preview with tiktoken**
- Uses `tiktoken` library for accurate token counting
- Supports multi-provider pricing (OpenAI vs Bedrock)
- Samples files to estimate total costs before analysis
- Shows detailed breakdown of tokens and pricing

### 2. **User Consent Flow**
- Automatic cost preview before Phase 2.5 analysis
- Clear warnings for high-cost operations
- User confirmation required to proceed
- Option to skip preview for automated usage

### 3. **Standalone Cost Preview Command**
- Preview costs without running analysis
- Compare pricing between providers
- Adjustable sample size for estimation accuracy

## 🚀 Usage Examples

### Basic Analysis with Cost Preview
```bash
# Standard analysis with cost preview and consent
python cli.py analyze https://github.com/owner/repo --phase 2.5 --provider openai
```

### Standalone Cost Preview
```bash
# Preview costs without running analysis
python cli.py cost-preview https://github.com/owner/repo --provider openai
python cli.py cost-preview https://github.com/owner/repo --provider bedrock --sample-size 10
```

### Skip Cost Preview (Automated Usage)
```bash
# Skip cost preview for CI/CD or automated scripts
python cli.py analyze https://github.com/owner/repo --phase 2.5 --provider openai --skip-cost-preview
```

### Token Analysis with Provider Pricing
```bash
# Analyze tokens with specific provider pricing
python cli.py analyze-tokens manifest.json --provider openai
python cli.py analyze-tokens manifest.json --provider bedrock
```

## 💰 Cost Comparison Example

For Flask repository analysis (116 files):

| Provider | Model | Estimated Cost | Cost per File |
|----------|-------|----------------|---------------|
| OpenAI   | gpt-4o-mini | $0.0136 | $0.0001 |
| Bedrock  | claude-3.5-sonnet | $0.3001 | $0.0026 |

**OpenAI is ~22x cheaper** for this type of analysis!

## 🔧 Technical Details

### Token Analysis Enhancement
- **Multi-provider pricing table**: Supports OpenAI and Bedrock pricing
- **Accurate token counting**: Uses tiktoken with cl100k_base encoding
- **Smart sampling**: Analyzes sample files to estimate total costs
- **Confidence levels**: High/Medium/Low based on sample size

### Cost Preview Algorithm
1. **Sample Analysis**: Analyzes 3-5 files by default
2. **Token Calculation**: Uses tiktoken for precise token counts
3. **Cost Estimation**: Applies provider-specific pricing
4. **Extrapolation**: Estimates total cost based on sample average
5. **Confidence Scoring**: Based on sample size and analysis success

### User Consent Flow
```
📋 Generate base manifest (always free)
↓
🔍 Analyze sample files for cost preview
↓
💰 Display cost estimate and breakdown
↓
❓ Request user consent (unless --skip-cost-preview)
↓
🧠 Proceed with LLM analysis (if approved)
```

## ⚠️ Cost Warnings

- **🚨 Very High Cost**: > $5.00 USD
- **⚠️ High Cost**: > $1.00 USD  
- **⚠️ Moderate Cost**: > $0.10 USD
- **✅ Low Cost**: ≤ $0.10 USD

## 🛠️ Configuration

The system automatically uses provider pricing from `config.yaml`:

```yaml
llm:
  default_provider: "openai"  # or "bedrock"
  
  openai:
    model: "gpt-4o-mini"
    # Pricing: $0.15/1M input tokens, $0.60/1M output tokens
  
  bedrock:
    model: "anthropic.claude-3-5-sonnet-20240620-v1:0"
    # Pricing: $3.00/1M input tokens, $15.00/1M output tokens
```

## 🔄 Backward Compatibility

- **Phase 1**: No changes (always free)
- **Phase 1.5**: Enhanced with provider-specific pricing
- **Phase 2**: No changes (Bedrock only)
- **Phase 2.5**: Enhanced with cost preview and consent
- **All existing commands**: Still work as before

## 💡 Best Practices

1. **Always preview costs** for new repositories
2. **Use OpenAI** for cost-effective analysis
3. **Use Bedrock** for highest quality analysis
4. **Use `--skip-cost-preview`** only for trusted automated workflows
5. **Adjust sample size** for better cost estimates on diverse repositories

## 🎉 Benefits

- **Cost Control**: No surprise charges from expensive LLM calls
- **Provider Choice**: Easy comparison between OpenAI and Bedrock
- **Transparency**: Clear breakdown of estimated costs
- **Flexibility**: Skip preview for automation, detailed preview for manual use
- **Accuracy**: tiktoken provides industry-standard token counting
