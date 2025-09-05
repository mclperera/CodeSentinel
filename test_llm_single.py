"""
Simple test script for LLM functionality with a single file
"""

import sys
import os
import time
sys.path.insert(0, 'src')

from llm_analyzer import LLMAnalyzer, LLMResponse
from github_analyzer import FileInfo
import yaml

def test_single_file_analysis():
    """Test LLM analysis on a single file"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create LLM analyzer
    print("🧠 Initializing LLM analyzer...")
    llm_analyzer = LLMAnalyzer(config)
    
    # Create a test file
    test_file = FileInfo(
        path="test_calculator.py",
        blob_sha="test123",
        size=500,
        extension=".py"
    )
    
    test_content = '''
def add(a, b):
    """Add two numbers together"""
    return a + b

def subtract(a, b):
    """Subtract second number from first"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide first number by second"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

if __name__ == "__main__":
    print("Simple Calculator")
    print("1 + 2 =", add(1, 2))
    print("5 - 3 =", subtract(5, 3))
    print("4 * 6 =", multiply(4, 6))
    print("8 / 2 =", divide(8, 2))
'''
    
    print("📋 Analyzing test file...")
    result = llm_analyzer.analyze_file_purpose(test_file, test_content)
    
    print("✅ Analysis complete!")
    print(f"Purpose: {result.purpose}")
    print(f"Category: {result.category}")
    print(f"Confidence: {result.confidence}")
    print(f"Security Relevance: {result.security_relevance}")
    print(f"Reasoning: {result.reasoning}")

if __name__ == "__main__":
    # Wait a bit for rate limiting to clear
    print("⏳ Waiting 30 seconds for rate limiting to clear...")
    time.sleep(30)
    
    try:
        test_single_file_analysis()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
