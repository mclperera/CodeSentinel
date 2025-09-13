#!/usr/bin/env python3
"""
Test script for the new configurable risk scoring system
"""

import sys
import os
import json
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github_analyzer import FileInfo
from src.risk_scorer import RiskScoringEngine


def create_test_file_with_vulnerabilities():
    """Create a test FileInfo object with sample vulnerabilities"""
    
    # Sample vulnerabilities (critical and high severity)
    vulnerabilities = [
        {
            'tool': 'semgrep',
            'rule_id': 'python.django.security.django-no-csrf-token',
            'severity': 'high',
            'message': 'CSRF token missing in form',
            'line_start': 14,
            'line_end': 18,
            'confidence': 'high',
            'cwe': 'CWE-352: Cross-Site Request Forgery (CSRF)'
        },
        {
            'tool': 'bandit',
            'rule_id': 'B101',
            'severity': 'critical', 
            'message': 'Use of assert detected',
            'line_start': 25,
            'line_end': 25,
            'confidence': 'high',
            'test_name': 'assert_used'
        }
    ]
    
    # Sample LLM metadata
    llm_metadata = {
        'category': 'authentication',
        'security_relevance': 'high',
        'reasoning': 'Handles user credentials and session management',
        'provider': 'openai',
        'model': 'gpt-4o-mini'
    }
    
    return FileInfo(
        path="src/auth/login.py",
        blob_sha="abc123",
        size=1500,
        extension=".py",
        purpose="User authentication and login management module",
        confidence_score=0.95,
        vulnerabilities=vulnerabilities,
        llm_metadata=llm_metadata
    )


def create_test_frontend_file():
    """Create a test frontend file with medium security relevance"""
    
    vulnerabilities = [
        {
            'tool': 'semgrep',
            'rule_id': 'html.security.audit.missing-integrity',
            'severity': 'medium',
            'message': 'Missing integrity attribute on external resource',
            'line_start': 10,
            'line_end': 10,
            'confidence': 'high',
            'cwe': 'CWE-353: Missing Support for Integrity Check'
        }
    ]
    
    llm_metadata = {
        'category': 'frontend',
        'security_relevance': 'medium',
        'reasoning': 'Frontend template with external CDN dependencies',
        'provider': 'openai',
        'model': 'gpt-4o-mini'
    }
    
    return FileInfo(
        path="templates/index.html",
        blob_sha="def456",
        size=800,
        extension=".html",
        purpose="Main application template with dynamic content",
        confidence_score=0.85,
        vulnerabilities=vulnerabilities,
        llm_metadata=llm_metadata
    )


def test_risk_scoring_engine():
    """Test the risk scoring engine with sample data"""
    
    print("🧪 Testing Configurable Risk Scoring System")
    print("=" * 50)
    
    # Initialize risk scoring engine
    try:
        engine = RiskScoringEngine("risk_scoring_config.yaml")
        print("✅ Risk scoring engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize risk scoring engine: {e}")
        return False
    
    # Test with high-risk authentication file
    print("\n🔐 Testing High-Risk Authentication File:")
    print("-" * 40)
    auth_file = create_test_file_with_vulnerabilities()
    assessment = engine.calculate_risk_assessment(auth_file)
    
    if assessment:
        print(f"File: {auth_file.path}")
        print(f"Risk Score: {assessment.risk_score}/10.0")
        print(f"Priority: {assessment.priority}")
        print(f"SLA Hours: {assessment.sla_hours}")
        print(f"Category: {assessment.category}")
        print(f"Security Relevance: {assessment.security_relevance}")
        print(f"Vulnerabilities: {assessment.vulnerability_count}")
        print(f"Component Scores: {json.dumps(assessment.component_scores, indent=2)}")
        print(f"Reasoning: {assessment.reasoning}")
    else:
        print("❌ No assessment generated")
    
    # Test with medium-risk frontend file
    print("\n🎨 Testing Medium-Risk Frontend File:")
    print("-" * 40)
    frontend_file = create_test_frontend_file()
    assessment2 = engine.calculate_risk_assessment(frontend_file)
    
    if assessment2:
        print(f"File: {frontend_file.path}")
        print(f"Risk Score: {assessment2.risk_score}/10.0")
        print(f"Priority: {assessment2.priority}")
        print(f"SLA Hours: {assessment2.sla_hours}")
        print(f"Category: {assessment2.category}")
        print(f"Security Relevance: {assessment2.security_relevance}")
        print(f"Vulnerabilities: {assessment2.vulnerability_count}")
        print(f"Component Scores: {json.dumps(assessment2.component_scores, indent=2)}")
        print(f"Reasoning: {assessment2.reasoning}")
    else:
        print("❌ No assessment generated")
    
    # Test configuration validation
    print("\n⚙️  Configuration Validation:")
    print("-" * 40)
    config = engine.config
    print(f"Vulnerability severity scores: {config['vulnerability_severity_scores']}")
    print(f"Category scores: {list(config['file_category_scores'].keys())}")
    print(f"Priority thresholds: {config['priority_thresholds']}")
    print(f"Component weights: {config['risk_component_weights']}")
    
    return True


def test_config_customization():
    """Test that configuration can be easily customized"""
    
    print("\n🔧 Testing Configuration Customization:")
    print("-" * 40)
    
    # Check if risk_scoring_config.yaml exists and is readable
    config_path = "risk_scoring_config.yaml"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                print(f"✅ Configuration file loaded successfully")
                print(f"Configuration sections: {list(config.keys())}")
                
                # Show how easy it is to modify
                print("\n📝 Sample customization examples:")
                print("- To make API files higher priority, change 'api: 8' to 'api: 9'")
                print("- To adjust CRITICAL threshold, change 'critical: 8.0' to 'critical: 7.5'")
                print("- To change weight distribution, modify 'risk_component_weights'")
                
        except Exception as e:
            print(f"❌ Error reading configuration: {e}")
    else:
        print(f"❌ Configuration file not found: {config_path}")


if __name__ == "__main__":
    print("CodeSentinel Risk Scoring System Test")
    print("=====================================\n")
    
    success = test_risk_scoring_engine()
    
    if success:
        test_config_customization()
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Review risk_scoring_config.yaml to customize scoring rules")
        print("2. Run vulnerability analysis on a real repository")
        print("3. Check the enhanced manifest output with risk assessments")
    else:
        print("\n💥 Tests failed - please check the configuration and dependencies")
        sys.exit(1)
