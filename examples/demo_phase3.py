#!/usr/bin/env python3
"""
Phase 3 Demo Script - Vulnerability Scanning Integration
Demonstrates Semgrep and Bandit integration with CodeSentinel
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Demonstrate Phase 3 vulnerability scanning capabilities"""
    
    print("🔒 CodeSentinel Phase 3 - Vulnerability Scanning Demo")
    print("=" * 60)
    
    # Test 1: Security Tool Manager
    print("\n1️⃣ Testing Security Tool Installation")
    print("-" * 40)
    
    try:
        from src.vulnerability_scanner import SecurityToolManager
        
        tool_manager = SecurityToolManager()
        print("🔧 Checking and installing security tools...")
        
        tool_status = tool_manager.check_and_install_tools()
        
        for tool, status in tool_status.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {tool}: {'Available' if status else 'Not available'}")
        
        if all(tool_status.values()):
            print("\n🎉 All tools are ready for vulnerability scanning!")
        else:
            print("\n⚠️  Some tools are missing. Install with:")
            print("   pip install semgrep bandit[toml]")
            return
            
    except ImportError as e:
        print(f"❌ Failed to import vulnerability scanner: {e}")
        return
    except Exception as e:
        print(f"❌ Tool check failed: {e}")
        return
    
    # Test 2: Small Repository Demo
    print("\n2️⃣ Running Vulnerability Scan Demo")
    print("-" * 40)
    
    # Use a small, well-known repository for testing
    test_repo = "https://github.com/octocat/Spoon-Knife"
    
    try:
        import yaml
        from src.github_analyzer import GitHubAnalyzer
        from src.vulnerability_scanner import run_vulnerability_analysis
        
        # Load config
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print(f"📥 Analyzing repository: {test_repo}")
        
        # Generate basic manifest
        analyzer = GitHubAnalyzer()
        manifest = analyzer.generate_manifest(test_repo)
        
        print(f"📁 Found {len(manifest.files)} files")
        
        # Run vulnerability analysis
        print("🔍 Running vulnerability scans...")
        enhanced_manifest, scan_results = run_vulnerability_analysis(
            test_repo, manifest, config
        )
        
        # Display results
        total_vulns = sum(len(f.vulnerabilities) for f in enhanced_manifest.files)
        files_with_vulns = sum(1 for f in enhanced_manifest.files if f.vulnerabilities)
        
        print(f"\n📊 Scan Results:")
        print(f"   Total vulnerabilities: {total_vulns}")
        print(f"   Files with vulnerabilities: {files_with_vulns}/{len(enhanced_manifest.files)}")
        
        if total_vulns > 0:
            print(f"\n🛡️  Vulnerability Details:")
            for file_info in enhanced_manifest.files:
                if file_info.vulnerabilities:
                    print(f"   📄 {file_info.path}: {len(file_info.vulnerabilities)} issues")
                    for vuln in file_info.vulnerabilities[:2]:  # Show first 2
                        print(f"      🚨 {vuln['tool']}: {vuln['severity']} - {vuln['message'][:60]}...")
        else:
            print("✅ No vulnerabilities found in this repository!")
        
        print(f"\n📊 Scanner Details:")
        semgrep_files = len(scan_results.get('semgrep_findings', {}))
        bandit_files = len(scan_results.get('bandit_findings', {}))
        print(f"   Semgrep scanned files with findings: {semgrep_files}")
        print(f"   Bandit scanned files with findings: {bandit_files}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 3: CLI Integration Demo
    print("\n3️⃣ CLI Integration Examples")
    print("-" * 40)
    
    print("🖥️  You can now use these commands:")
    print()
    print("   # Test vulnerability scanner:")
    print("   python cli.py test-vulnerability-scanner")
    print()
    print("   # Run Phase 3 analysis:")
    print(f"   python cli.py analyze {test_repo} --phase 3")
    print()
    print("   # Add vulnerability scanning to any phase:")
    print(f"   python cli.py analyze {test_repo} --phase 2.5 --scan-vulnerabilities")
    print()
    print("   # Use specific scanners only:")
    print(f"   python cli.py analyze {test_repo} --phase 3 --scanners semgrep")
    print(f"   python cli.py analyze {test_repo} --phase 3 --scanners bandit")
    print()
    
    print("🎉 Phase 3 Demo Complete!")
    print("🔒 CodeSentinel now supports comprehensive vulnerability scanning!")


if __name__ == "__main__":
    main()
