# Configurable Risk Scoring System

## Overview

The CodeSentinel risk scoring system provides intelligent, configurable vulnerability prioritization based on:

- **Vulnerability severity** (40% weight by default)
- **File category** from LLM analysis (35% weight by default) 
- **Security relevance** from LLM analysis (25% weight by default)

## Quick Start

The system automatically calculates risk scores (0-10) and assigns priority levels:

- **CRITICAL (8-10)**: 4-hour SLA
- **HIGH (6-8)**: 24-hour SLA  
- **MEDIUM (4-6)**: 72-hour SLA
- **LOW (2-4)**: 1-week SLA
- **INFO (0-2)**: No SLA

## Configuration

All scoring rules are defined in `risk_scoring_config.yaml`:

```yaml
# Vulnerability severity scores
vulnerability_severity_scores:
  critical: 10
  high: 7
  medium: 4
  low: 1

# File category risk scores
file_category_scores:
  authentication: 10    # Highest risk
  api: 8               # High risk
  data-processing: 7   # High risk
  config: 6            # Medium-high
  frontend: 4          # Medium
  build: 3             # Low-medium
  test: 2              # Low
  documentation: 1     # Lowest
  other: 3             # Default

# Security relevance scores
security_relevance_scores:
  high: 10
  medium: 5
  low: 2

# Component weights (must sum to 1.0)
risk_component_weights:
  vulnerability_severity: 0.40
  file_category: 0.35
  security_relevance: 0.25

# Priority thresholds
priority_thresholds:
  critical: 8.0
  high: 6.0
  medium: 4.0
  low: 2.0
```

## Usage

The risk scoring is automatically integrated into vulnerability scanning:

```python
from src.vulnerability_scanner import run_vulnerability_analysis

# Run analysis with risk scoring
enhanced_manifest, scan_results = run_vulnerability_analysis(repo_url, manifest, config)

# Access risk assessments
for risk_assessment in scan_results['risk_assessments']:
    print(f"File: {risk_assessment['file_path']}")
    print(f"Risk Score: {risk_assessment['risk_score']}")
    print(f"Priority: {risk_assessment['priority']}")
    print(f"SLA: {risk_assessment['sla_hours']} hours")
```

## Customization Examples

### Make API files higher priority:
```yaml
file_category_scores:
  api: 9  # Changed from 8
```

### Lower the CRITICAL threshold:
```yaml
priority_thresholds:
  critical: 7.5  # Changed from 8.0
```

### Adjust component weights:
```yaml
risk_component_weights:
  vulnerability_severity: 0.50  # Increase focus on severity
  file_category: 0.30           # Reduce category weight
  security_relevance: 0.20      # Reduce relevance weight
```

## Output Format

Enhanced manifest files now include:

```json
{
  "path": "src/auth/login.py",
  "vulnerabilities": [...],
  "risk_score": 8.5,
  "priority": "CRITICAL",
  "sla_hours": 4
}
```

Scan results include detailed risk assessments:

```json
{
  "risk_assessments": [
    {
      "file_path": "src/auth/login.py",
      "risk_score": 8.5,
      "priority": "CRITICAL",
      "sla_hours": 4,
      "vulnerability_count": 2,
      "category": "authentication",
      "security_relevance": "high",
      "component_scores": {
        "vulnerability_severity": 7.5,
        "file_category": 10.0,
        "security_relevance": 10.0
      },
      "reasoning": "2 vulnerabilities found: 1 high, 1 critical; High-impact authentication file"
    }
  ]
}
```
