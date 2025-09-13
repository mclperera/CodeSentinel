# Risk Scoring Tests

This directory contains tests for the configurable risk scoring system.

## Test Files

- `test_risk_scoring.py` - Basic functionality tests with synthetic data
- `test_real_data.py` - Tests using real vulnerability data from flask-analysis.json

## Running Tests

From the project root directory:

```bash
# Activate virtual environment
source venv/bin/activate

# Run basic functionality test
python tests/risk_scoring/test_risk_scoring.py

# Run real data test (requires flask-analysis.json in project root)
python tests/risk_scoring/test_real_data.py
```

## What These Tests Validate

1. **Configuration Loading**: Ensures risk_scoring_config.yaml is properly loaded
2. **Score Calculation**: Validates risk score calculations across different scenarios
3. **Priority Assignment**: Confirms priority levels are assigned correctly
4. **Component Weighting**: Tests that component weights are applied properly
5. **Real Data Integration**: Validates the system works with actual vulnerability data

## Expected Output

Both tests should complete successfully and display:
- Risk scores for sample files
- Priority assignments (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Component score breakdowns
- Configuration validation
- Reasoning for risk assessments
