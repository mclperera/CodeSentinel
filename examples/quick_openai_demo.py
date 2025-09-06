#!/usr/bin/env python3
"""
Quick OpenAI Analysis Demo - Analyze specific files to show the quality of OpenAI analysis
"""

import yaml
import json
from src.github_analyzer import FileInfo, GitHubAnalyzer
from src.multi_llm_analyzer import MultiProviderLLMAnalyzer

def analyze_codesentinel_files():
    """Analyze our own CodeSentinel files to demonstrate OpenAI analysis quality"""
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize OpenAI analyzer
    analyzer = MultiProviderLLMAnalyzer(config, provider='openai')
    
    # Test connection
    if not analyzer.test_connection():
        print("❌ OpenAI connection failed")
        return
    
    print("🧠 CodeSentinel File Analysis with OpenAI")
    print("=" * 50)
    
    # Files to analyze from our project
    test_files = {
        'src/github_analyzer.py': 'Core GitHub API integration and repository analysis module',
        'src/token_analyzer.py': 'Token counting and cost estimation using tiktoken',  
        'src/multi_llm_analyzer.py': 'Multi-provider LLM analysis with OpenAI and Bedrock support',
        'cli.py': 'Command-line interface for CodeSentinel analysis phases',
        'config.yaml': 'Configuration file with multi-provider LLM settings'
    }
    
    results = []
    
    for file_path, expected_description in test_files.items():
        print(f"\n📄 Analyzing: {file_path}")
        print(f"Expected: {expected_description}")
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create FileInfo
            file_info = FileInfo(
                path=file_path,
                blob_sha="local",
                size=len(content),
                extension=file_path.split('.')[-1]
            )
            
            # Analyze with OpenAI
            response = analyzer.analyze_file_purpose(file_info, content)
            
            print(f"🤖 OpenAI Analysis:")
            print(f"   Purpose: {response.purpose}")
            print(f"   Category: {response.category}")
            print(f"   Security: {response.security_relevance}")
            print(f"   Confidence: {response.confidence:.2f}")
            print(f"   Provider: {response.provider} ({response.model})")
            
            if response.reasoning:
                print(f"   Reasoning: {response.reasoning}")
            
            # Store result
            results.append({
                'file': file_path,
                'expected': expected_description,
                'openai_analysis': {
                    'purpose': response.purpose,
                    'category': response.category,
                    'security_relevance': response.security_relevance,
                    'confidence': response.confidence,
                    'reasoning': response.reasoning,
                    'provider': response.provider,
                    'model': response.model
                }
            })
            
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {str(e)}")
    
    # Save results as a sample manifest
    sample_manifest = {
        'repository': {
            'name': 'CodeSentinel',
            'url': 'https://github.com/mclperera/CodeSentinel',
            'analysis_timestamp': '2025-09-07T00:25:00Z',
            'provider': 'openai',
            'model': 'gpt-4o-mini'
        },
        'files_analyzed': len(results),
        'analysis_results': results
    }
    
    # Save to tests/data directory
    import os
    os.makedirs('tests/data', exist_ok=True)
    output_file = 'tests/data/codesentinel_openai_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(sample_manifest, f, indent=2)
    
    print(f"\n✅ Analysis complete! Results saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Files analyzed: {len(results)}")
    print(f"   Average confidence: {sum(r['openai_analysis']['confidence'] for r in results) / len(results):.2f}")
    
    # Category breakdown
    categories = {}
    security_levels = {}
    
    for result in results:
        category = result['openai_analysis']['category']
        security = result['openai_analysis']['security_relevance']
        
        categories[category] = categories.get(category, 0) + 1
        security_levels[security] = security_levels.get(security, 0) + 1
    
    print(f"\n📋 Categories detected:")
    for cat, count in categories.items():
        print(f"   {cat}: {count} files")
    
    print(f"\n🔒 Security levels:")
    for level, count in security_levels.items():
        print(f"   {level}: {count} files")

if __name__ == "__main__":
    analyze_codesentinel_files()
