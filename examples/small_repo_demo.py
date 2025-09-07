#!/usr/bin/env python3
"""
Small Repository Analysis Demo
Demonstrates the refactored prompts system on a small public repository
"""

import yaml
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github_analyzer import GitHubAnalyzer
from src.multi_llm_analyzer import MultiProviderLLMAnalyzer


def analyze_small_repo():
    """Analyze a small public repository to demonstrate the prompts in action"""
    
    print("🔍 Small Repository Analysis Demo")
    print("=" * 60)
    
    # Load config
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        print("Please ensure config.yaml exists and is properly formatted")
        return
    
    # Small test repositories
    test_repos = [
        {
            "name": "Hello World",
            "url": "https://github.com/octocat/Hello-World",
            "description": "GitHub's classic Hello World repository"
        },
        {
            "name": "Spoon Knife", 
            "url": "https://github.com/octocat/Spoon-Knife",
            "description": "Simple repository for testing forks"
        }
    ]
    
    # Initialize analyzers
    try:
        github_analyzer = GitHubAnalyzer()
        print("✅ GitHub analyzer initialized")
        
        # Try OpenAI first, fallback to analyzing without LLM if needed
        llm_analyzer = None
        provider_used = None
        
        try:
            llm_analyzer = MultiProviderLLMAnalyzer(config, provider='openai')
            if llm_analyzer.test_connection():
                provider_used = 'openai'
                print("✅ OpenAI analyzer initialized and connected")
            else:
                print("⚠️  OpenAI connection failed")
                llm_analyzer = None
        except Exception as e:
            print(f"⚠️  OpenAI initialization failed: {e}")
            
        # Try Bedrock as fallback
        if not llm_analyzer:
            try:
                llm_analyzer = MultiProviderLLMAnalyzer(config, provider='bedrock')
                if llm_analyzer.test_connection():
                    provider_used = 'bedrock'
                    print("✅ Bedrock analyzer initialized and connected")
                else:
                    print("⚠️  Bedrock connection failed")
                    llm_analyzer = None
            except Exception as e:
                print(f"⚠️  Bedrock initialization failed: {e}")
        
        if not llm_analyzer:
            print("⚠️  No LLM provider available - will perform basic GitHub analysis only")
            
    except Exception as e:
        print(f"❌ Error initializing analyzers: {e}")
        return
    
    # Analyze each repository
    for repo_info in test_repos:
        print(f"\n🔍 Analyzing: {repo_info['name']}")
        print(f"📍 URL: {repo_info['url']}")
        print(f"📝 Description: {repo_info['description']}")
        print("-" * 50)
        
        try:
            # Generate base manifest
            print("📊 Generating GitHub manifest...")
            manifest = github_analyzer.generate_manifest(repo_info['url'])
            
            print(f"✅ Found {len(manifest.files)} files:")
            for file_info in manifest.files[:5]:  # Show first 5 files
                print(f"   📄 {file_info.path} ({file_info.size} bytes)")
            
            if len(manifest.files) > 5:
                print(f"   ... and {len(manifest.files) - 5} more files")
            
            # Enrich with LLM analysis if available
            if llm_analyzer:
                print(f"\n🧠 Enriching with {provider_used.upper()} analysis...")
                
                # Limit to small files for demo
                small_files = [f for f in manifest.files if f.size < 10000]  # < 10KB
                if small_files:
                    print(f"📊 Analyzing {len(small_files)} small files (< 10KB each)")
                    
                    # Create a subset manifest for analysis
                    subset_manifest = manifest
                    subset_manifest.files = small_files[:3]  # Limit to 3 files for demo
                    
                    enriched_manifest = llm_analyzer.enrich_manifest_with_llm_analysis(
                        subset_manifest, github_analyzer
                    )
                    
                    print(f"\n🎯 LLM Analysis Results:")
                    for file_info in enriched_manifest.files:
                        if hasattr(file_info, 'purpose') and file_info.purpose:
                            print(f"\n📄 {file_info.path}:")
                            print(f"   🎯 Purpose: {file_info.purpose}")
                            print(f"   📂 Category: {file_info.llm_metadata.get('category', 'unknown')}")
                            print(f"   🔒 Security: {file_info.llm_metadata.get('security_relevance', 'unknown')}")
                            print(f"   📊 Confidence: {file_info.confidence_score:.2f}")
                            if file_info.llm_metadata.get('reasoning'):
                                print(f"   💭 Reasoning: {file_info.llm_metadata['reasoning']}")
                else:
                    print("⚠️  No small files found for LLM analysis")
            
            # Save results
            output_dir = f"analysis-results/{repo_info['name'].lower().replace(' ', '_')}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save manifest
            manifest_file = f"{output_dir}/manifest.json"
            github_analyzer.save_manifest(manifest, manifest_file)
            print(f"\n💾 Results saved to: {manifest_file}")
            
        except Exception as e:
            print(f"❌ Error analyzing {repo_info['name']}: {e}")
            continue
    
    print(f"\n🎉 Analysis complete!")
    if provider_used:
        print(f"🧠 LLM Provider used: {provider_used.upper()}")
    print(f"📁 Results saved in: analysis-results/")


def main():
    """Main function"""
    try:
        analyze_small_repo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
