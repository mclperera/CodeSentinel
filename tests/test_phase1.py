#!/usr/bin/env python3
"""
Test script for Phase 1 GitHub integration
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_phase1():
    """Test Phase 1 functionality"""
    print("🧪 Testing Phase 1 - GitHub Integration")
    print("=" * 50)
    
    try:
        from github_analyzer import GitHubAnalyzer
        
        # Initialize analyzer
        print("1. Initializing GitHub analyzer...")
        analyzer = GitHubAnalyzer()
        print("✅ Analyzer initialized successfully")
        
        # Test connection
        print("\n2. Testing GitHub connection...")
        user = analyzer.github.get_user()
        rate_limit = analyzer.github.get_rate_limit()
        print(f"✅ Connected as: {user.login}")
        print(f"✅ Rate limit remaining: {rate_limit.core.remaining if hasattr(rate_limit, 'core') else 'N/A'}")
        
        # Test with a small public repository
        print("\n3. Testing repository analysis...")
        test_repo_url = "https://github.com/octocat/Hello-World"
        
        print(f"   Analyzing: {test_repo_url}")
        manifest = analyzer.generate_manifest(test_repo_url)
        
        print(f"✅ Repository: {manifest.repository.url}")
        print(f"✅ Default branch: {manifest.repository.default_branch}")
        print(f"✅ Commit SHA: {manifest.repository.commit_sha}")
        print(f"✅ Files found: {len(manifest.files)}")
        
        # Show file details
        if manifest.files:
            print(f"\n   Sample files:")
            for i, file_info in enumerate(manifest.files[:5]):
                print(f"   - {file_info.path} ({file_info.size} bytes, {file_info.extension})")
                if i >= 4:  # Show max 5 files
                    break
        
        # Save test manifest
        print("\n4. Saving manifest...")
        output_path = "test_manifest_phase1.json"
        analyzer.save_manifest(manifest, output_path)
        print(f"✅ Manifest saved to: {output_path}")
        
        # Test loading manifest
        print("\n5. Testing manifest loading...")
        loaded_manifest = analyzer.load_manifest(output_path)
        print(f"✅ Manifest loaded with {len(loaded_manifest.files)} files")
        
        print(f"\n🎉 Phase 1 testing completed successfully!")
        print(f"📄 Test manifest available at: {output_path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Run 'pip install -r requirements.txt' to install dependencies")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False


def test_cli():
    """Test CLI functionality"""
    print("\n🧪 Testing CLI Interface")
    print("=" * 50)
    
    try:
        import subprocess
        
        # Test CLI help
        print("1. Testing CLI help...")
        result = subprocess.run([sys.executable, "cli.py", "--help"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI help command works")
        else:
            print("❌ CLI help command failed")
            return False
        
        # Test connection command
        print("\n2. Testing connection command...")
        result = subprocess.run([sys.executable, "cli.py", "test-connection"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Connection test successful")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print("❌ Connection test failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ CLI testing error: {str(e)}")
        return False


if __name__ == "__main__":
    success = True
    
    # Test Phase 1 core functionality
    if not test_phase1():
        success = False
    
    # Test CLI interface
    if success and not test_cli():
        success = False
    
    if success:
        print(f"\n🎊 All tests passed! Phase 1 implementation complete.")
        print(f"\n📋 What was implemented:")
        print(f"   ✅ GitHub API integration module")
        print(f"   ✅ Repository discovery and branch detection") 
        print(f"   ✅ Blob extraction and file inventory system")
        print(f"   ✅ Initial manifest generation")
        print(f"   ✅ CLI interface for repository analysis")
        print(f"\n🚀 Ready for Phase 2: LLM Integration")
    else:
        print(f"\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
