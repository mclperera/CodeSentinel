#!/usr/bin/env python3
"""
Test the risk scoring system with real data from flask-analysis.json
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github_analyzer import FileInfo
from src.risk_scorer import RiskScoringEngine


def load_flask_vulnerable_files():
    """Load vulnerable files from flask-analysis.json"""
    
    try:
        with open('flask-analysis.json', 'r') as f:
            data = json.load(f)
        
        vulnerable_files = []
        for file_data in data['files']:
            if file_data.get('vulnerabilities') and len(file_data['vulnerabilities']) > 0:
                # Create FileInfo object
                file_info = FileInfo(
                    path=file_data['path'],
                    blob_sha=file_data['blob_sha'],
                    size=file_data['size'],
                    extension=file_data['extension'],
                    purpose=file_data.get('purpose'),
                    confidence_score=file_data.get('confidence_score'),
                    vulnerabilities=file_data['vulnerabilities'],
                    risk_score=file_data.get('risk_score'),
                    llm_metadata=file_data.get('llm_metadata', {})
                )
                vulnerable_files.append(file_info)
        
        return vulnerable_files
        
    except Exception as e:
        print(f"Error loading flask-analysis.json: {e}")
        return []


def test_with_real_data():
    """Test risk scoring with real Flask repository data"""
    
    print("🔍 Testing Risk Scoring with Real Flask Repository Data")
    print("=" * 60)
    
    # Load vulnerable files
    vulnerable_files = load_flask_vulnerable_files()
    
    if not vulnerable_files:
        print("❌ No vulnerable files found in flask-analysis.json")
        return
    
    print(f"📁 Found {len(vulnerable_files)} files with vulnerabilities")
    
    # Initialize risk scoring engine
    engine = RiskScoringEngine("risk_scoring_config.yaml")
    
    # Analyze each vulnerable file
    assessments = []
    for file_info in vulnerable_files[:5]:  # Test first 5 files
        assessment = engine.calculate_risk_assessment(file_info)
        if assessment:
            assessments.append((file_info, assessment))
    
    # Sort by risk score (highest first)
    assessments.sort(key=lambda x: x[1].risk_score, reverse=True)
    
    print("\n🚨 Top Vulnerable Files by Risk Score:")
    print("-" * 60)
    
    for i, (file_info, assessment) in enumerate(assessments, 1):
        print(f"\n{i}. {file_info.path}")
        print(f"   Risk Score: {assessment.risk_score}/10.0 ({assessment.priority})")
        print(f"   Category: {assessment.category} | Security Relevance: {assessment.security_relevance}")
        print(f"   Vulnerabilities: {assessment.vulnerability_count} | SLA: {assessment.sla_hours}h")
        print(f"   Reasoning: {assessment.reasoning[:80]}...")
        
        # Show vulnerability details
        severities = [v.get('severity', 'unknown') for v in file_info.vulnerabilities]
        severity_counts = {}
        for s in severities:
            severity_counts[s] = severity_counts.get(s, 0) + 1
        severity_summary = ", ".join([f"{count} {sev}" for sev, count in severity_counts.items()])
        print(f"   Vulnerability breakdown: {severity_summary}")
    
    # Show priority breakdown
    priority_counts = {}
    for _, assessment in assessments:
        priority = assessment.priority
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    print(f"\n📊 Priority Breakdown:")
    print("-" * 30)
    for priority, count in sorted(priority_counts.items()):
        print(f"   {priority}: {count} files")
    
    # Show how configuration affects scoring
    print(f"\n⚙️  Configuration Impact:")
    print("-" * 30)
    print("Current component weights:")
    weights = engine.config['risk_component_weights']
    for component, weight in weights.items():
        print(f"   {component}: {weight*100}%")


if __name__ == "__main__":
    test_with_real_data()
