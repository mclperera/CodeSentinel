#!/usr/bin/env python3
"""
CodeSentinel CLI - Phase 2
Command-line interface for GitHub repository analysis with LLM integration
"""

import click
import sys
import os
import yaml
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from github_analyzer import GitHubAnalyzer
from llm_analyzer import LLMAnalyzer
from token_analyzer import TokenAnalyzer


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """CodeSentinel - GitHub Repository Risk Analysis Tool
    
    Phase 1: Basic repository analysis and file inventory
    Phase 1.5: Token analysis and cost estimation  
    Phase 2: LLM-enhanced code understanding (Bedrock only)
    Phase 2.5: Multi-provider LLM analysis (OpenAI + Bedrock)
    Phase 3: Vulnerability scanning (Semgrep + Bandit)
    """
    pass


@cli.command()
@click.argument('repository_url')
@click.option('--output', '-o', default=None, help='Output manifest file path (defaults to config default)')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--phase', '-p', type=click.Choice(['1', '1.5', '2', '2.5', '3']), default='1', 
              help='Analysis phase: 1=Basic analysis, 1.5=Token analysis, 2=LLM (Bedrock), 2.5=Multi-provider LLM, 3=Vulnerability scanning')
@click.option('--aws-profile', default='bedrock-dev', help='AWS profile for Bedrock access')
@click.option('--provider', type=click.Choice(['openai', 'bedrock']), default=None, 
              help='LLM provider for Phase 2.5 (defaults to config setting)')
@click.option('--scan-vulnerabilities', is_flag=True, default=False,
              help='Run vulnerability scans (Semgrep & Bandit) regardless of phase')
@click.option('--scanners', default='semgrep,bandit', 
              help='Comma-separated list of scanners to run (semgrep,bandit)')
@click.option('--skip-cost-preview', is_flag=True, default=False,
              help='Skip cost preview and consent prompt for automated usage')
def analyze(repository_url, output, config, phase, aws_profile, provider, scan_vulnerabilities, scanners, skip_cost_preview):
    """Analyze a GitHub repository and generate a manifest"""
    click.echo(f"🔍 Analyzing repository: {repository_url} (Phase {phase})")
    
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Set default output path if not provided
        if output is None:
            output_config = config_data.get('output', {})
            default_dir = output_config.get('default_dir', '.')
            default_filename = output_config.get('manifest', 'manifest.json')
            output = os.path.join(default_dir, default_filename)
        
        # Initialize GitHub analyzer
        analyzer = GitHubAnalyzer(config_path=config)
        
        # Check if manifest file already exists for sequential enhancement
        if os.path.exists(output) and phase in ['1.5', '2', '2.5', '3', '4']:
            click.echo(f"📋 Loading existing manifest from {output} for Phase {phase} enhancement...")
            try:
                manifest = analyzer.load_manifest(output)
                click.echo(f"✅ Loaded existing manifest with {len(manifest.files)} files")
                
                # Verify this is the same repository
                if manifest.repository.url != repository_url:
                    click.echo(f"⚠️  Warning: Existing manifest is for different repository!")
                    click.echo(f"   Existing: {manifest.repository.url}")
                    click.echo(f"   Requested: {repository_url}")
                    overwrite = click.confirm("Do you want to overwrite with new repository analysis?", default=False)
                    if not overwrite:
                        click.echo("❌ Analysis cancelled. Use different output file or confirm overwrite.")
                        return
                    # Generate fresh manifest if user chooses to overwrite
                    click.echo("📋 Generating fresh manifest...")
                    manifest = analyzer.generate_manifest(repository_url)
                else:
                    click.echo(f"✅ Repository matches: {repository_url}")
                    
            except Exception as e:
                click.echo(f"⚠️  Could not load existing manifest: {e}")
                click.echo("📋 Generating fresh manifest...")
                manifest = analyzer.generate_manifest(repository_url)
        else:
            # Generate basic manifest (Phase 1 or no existing file)
            click.echo("📋 Generating base manifest...")
            manifest = analyzer.generate_manifest(repository_url)
        
        if phase == '1.5':
            # Token analysis (Phase 1.5)
            provider_name = provider or config_data.get('llm', {}).get('default_provider', 'openai')
            click.echo(f"🔢 Performing token analysis using {provider_name.upper()} pricing...")
            token_analyzer = TokenAnalyzer(config_data, provider=provider_name)
            file_stats, repo_stats = token_analyzer.analyze_repository_tokens(manifest, analyzer)
            
            # Save token analysis
            token_output = output.replace('.json', '_tokens.json')
            token_analyzer.save_token_analysis(file_stats, repo_stats, token_output)
            token_analyzer.print_token_summary(repo_stats)
            click.echo(f"📊 Token analysis saved to: {token_output}")
            
        elif phase == '2':
            # Original Bedrock-only LLM analysis (Phase 2)
            click.echo("🧠 Enhancing with Bedrock LLM analysis...")
            llm_analyzer = LLMAnalyzer(config_data, aws_profile=aws_profile)
            manifest = llm_analyzer.enrich_manifest_with_llm_analysis(manifest, analyzer)
            click.echo("✨ Bedrock LLM analysis complete!")
            
        elif phase == '2.5':
            # Multi-provider LLM analysis (Phase 2.5) with cost preview and consent
            provider_name = provider or config_data.get('llm', {}).get('default_provider', 'openai')
            
            if not skip_cost_preview:
                # Initialize token analyzer for cost preview
                from src.token_analyzer import TokenAnalyzer
                token_analyzer = TokenAnalyzer(config_data, provider=provider_name)
                
                # Get cost preview
                click.echo(f"🔍 Analyzing cost preview for {provider_name.upper()} provider...")
                cost_preview = token_analyzer.get_cost_preview(manifest, sample_size=5)
                
                # Display cost preview
                click.echo(f"\n💰 Cost Preview for LLM Analysis:")
                click.echo(f"📁 Total files to analyze: {cost_preview['total_files']}")
                click.echo(f"🔬 Sample analyzed: {cost_preview['sample_analyzed']} files")
                click.echo(f"🤖 Provider: {cost_preview['provider'].upper()}")
                click.echo(f"🧠 Model: {cost_preview['model']}")
                
                if cost_preview.get('error'):
                    click.echo(f"⚠️  Warning: {cost_preview['error']}")
                    if cost_preview['confidence'] == 'error':
                        click.echo("❌ Cannot proceed without cost estimation")
                        return
                
                if cost_preview['estimated_total_cost'] > 0:
                    click.echo(f"💵 Estimated cost: ${cost_preview['estimated_total_cost']:.4f} USD")
                    click.echo(f"📊 Average tokens per file: {cost_preview.get('avg_tokens_per_file', 0):.0f}")
                    click.echo(f"🎯 Total estimated tokens: {cost_preview.get('estimated_total_tokens', 0):,.0f}")
                    click.echo(f"📈 Confidence level: {cost_preview['confidence']}")
                    
                    # Show pricing breakdown
                    pricing = cost_preview.get('pricing', {})
                    if pricing:
                        click.echo(f"\n💸 Pricing Details:")
                        click.echo(f"   Input tokens: ${pricing.get('input_per_1k', 0):.6f} per 1K tokens")
                        click.echo(f"   Output tokens: ${pricing.get('output_per_1k', 0):.6f} per 1K tokens")
                    
                    # Cost threshold warnings
                    if cost_preview['estimated_total_cost'] > 1.0:
                        click.echo(f"\n⚠️  HIGH COST WARNING: Estimated cost exceeds $1.00")
                    elif cost_preview['estimated_total_cost'] > 0.10:
                        click.echo(f"\n⚠️  Cost notice: Estimated cost exceeds $0.10")
                    
                    # Get user consent
                    click.echo(f"\n❓ Do you want to proceed with the analysis?")
                    consent = click.confirm("Continue with LLM analysis?", default=False)
                    
                    if not consent:
                        click.echo("❌ Analysis cancelled by user")
                        click.echo(f"💡 Tip: You can run 'python cli.py analyze {repository_url} --phase 1' for free basic analysis")
                        return
                    
                    click.echo("✅ User consent confirmed, proceeding with analysis...")
                else:
                    click.echo("ℹ️  No cost estimated (possibly no supported files found)")
                    consent = click.confirm("Continue anyway?", default=True)
                    if not consent:
                        click.echo("❌ Analysis cancelled by user")
                        return
            else:
                click.echo(f"⏭️  Skipping cost preview (--skip-cost-preview flag used)")
            
            click.echo(f"\n🧠 Enhancing with multi-provider LLM analysis using {provider_name.upper()}...")
            
            from src.multi_llm_analyzer import MultiProviderLLMAnalyzer
            llm_analyzer = MultiProviderLLMAnalyzer(config_data, provider=provider)
            
            # Test connection first
            if not llm_analyzer.test_connection():
                click.echo(f"❌ Failed to connect to {provider_name.upper()} provider")
                return
            
            manifest = llm_analyzer.enrich_manifest_with_llm_analysis(manifest, analyzer)
            click.echo(f"✨ Multi-provider LLM analysis complete using {provider_name.upper()}!")
        
        # Phase 3: Vulnerability Scanning
        if phase == '3' or scan_vulnerabilities:
            click.echo("\n🔒 Phase 3: Running vulnerability scans...")
            
            # Parse scanners option
            enabled_scanners = [s.strip() for s in scanners.split(',') if s.strip()]
            click.echo(f"🛡️  Enabled scanners: {', '.join(enabled_scanners)}")
            
            # Update config to enable/disable scanners based on user choice
            vuln_config = config_data.get('vulnerability_scanning', {})
            if 'semgrep' in enabled_scanners:
                vuln_config.setdefault('semgrep', {})['enabled'] = True
            else:
                vuln_config.setdefault('semgrep', {})['enabled'] = False
                
            if 'bandit' in enabled_scanners:
                vuln_config.setdefault('bandit', {})['enabled'] = True
            else:
                vuln_config.setdefault('bandit', {})['enabled'] = False
            
            try:
                from src.vulnerability_scanner import run_vulnerability_analysis
                
                click.echo("🔧 Checking and installing security tools...")
                enhanced_manifest, scan_results = run_vulnerability_analysis(
                    repository_url, manifest, config_data
                )
                
                manifest = enhanced_manifest
                
                # Display vulnerability summary
                total_vulnerabilities = sum(len(f.vulnerabilities) for f in manifest.files)
                files_with_vulns = sum(1 for f in manifest.files if f.vulnerabilities)
                
                click.echo(f"✅ Vulnerability analysis complete!")
                click.echo(f"🛡️  Total vulnerabilities found: {total_vulnerabilities}")
                click.echo(f"📁 Files with vulnerabilities: {files_with_vulns}/{len(manifest.files)}")
                
                # Show severity breakdown
                severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                tool_counts = {}
                
                for file_info in manifest.files:
                    for vuln in file_info.vulnerabilities:
                        severity = vuln.get('severity', 'low')
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                        
                        tool = vuln.get('tool', 'unknown')
                        tool_counts[tool] = tool_counts.get(tool, 0) + 1
                
                if total_vulnerabilities > 0:
                    click.echo(f"\n🚨 Severity breakdown:")
                    for severity, count in severity_counts.items():
                        if count > 0:
                            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
                            click.echo(f"   {icon} {severity.capitalize()}: {count}")
                    
                    click.echo(f"\n🔧 Scanner breakdown:")
                    for tool, count in tool_counts.items():
                        click.echo(f"   {tool}: {count} findings")
                
            except ImportError as e:
                click.echo(f"❌ Vulnerability scanner not available: {e}")
                click.echo("💡 Try: pip install semgrep bandit[toml]")
            except Exception as e:
                click.echo(f"❌ Vulnerability scanning failed: {e}")
                click.echo("⚠️  Continuing with analysis without vulnerability data...")
        
        # Save manifest
        analyzer.save_manifest(manifest, output)
        
        # Display results
        click.echo("✅ Analysis complete!")
        click.echo(f"📄 Manifest saved to: {output}")
        click.echo(f"🏛️  Repository: {manifest.repository.url}")
        click.echo(f"🌿 Default branch: {manifest.repository.default_branch}")
        click.echo(f"📝 Commit SHA: {manifest.repository.commit_sha}")
        click.echo(f"📁 Files analyzed: {len(manifest.files)}")
        
        if phase in ['2', '2.5']:
            # Show LLM analysis summary for both Phase 2 and 2.5
            categorized_files = {}
            analyzed_files = 0
            
            for file_info in manifest.files:
                if hasattr(file_info, 'purpose') and file_info.purpose:
                    analyzed_files += 1
                    llm_metadata = getattr(file_info, 'llm_metadata', {})
                    category = llm_metadata.get('category', 'other')
                    categorized_files[category] = categorized_files.get(category, 0) + 1
            
            provider_display = provider_name.upper() if phase == '2.5' else 'BEDROCK'
            click.echo(f"\n🧠 LLM Analysis Summary ({provider_display}):")
            click.echo(f"📊 Files analyzed: {analyzed_files}/{len(manifest.files)}")
            
            if categorized_files:
                click.echo("\n📋 Purpose categories:")
                for category, count in sorted(categorized_files.items()):
                    click.echo(f"  {category}: {count} files")
        
        # Show vulnerability summary if Phase 3 was run
        if phase == '3' or scan_vulnerabilities:
            total_vulns = sum(len(f.vulnerabilities) for f in manifest.files)
            if total_vulns > 0:
                high_risk_files = [f for f in manifest.files if len(f.vulnerabilities) >= 3]
                click.echo(f"\n🛡️  Vulnerability Summary:")
                click.echo(f"   Total findings: {total_vulns}")
                click.echo(f"   High-risk files: {len(high_risk_files)} (3+ vulnerabilities)")
        
        # Show file type breakdown
        extensions = {}
        for file_info in manifest.files:
            ext = file_info.extension
            extensions[ext] = extensions.get(ext, 0) + 1
        
        click.echo("\n📊 File type breakdown:")
        for ext, count in sorted(extensions.items()):
            click.echo(f"  {ext}: {count} files")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('repository_url')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--provider', type=click.Choice(['openai', 'bedrock']), default=None, 
              help='LLM provider to estimate costs for (defaults to config setting)')
@click.option('--sample-size', '-s', default=5, help='Number of files to sample for cost estimation')
def cost_preview(repository_url, config, provider, sample_size):
    """Preview estimated costs for LLM analysis without running it"""
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        provider_name = provider or config_data.get('llm', {}).get('default_provider', 'openai')
        
        click.echo(f"💰 Generating cost preview for: {repository_url}")
        click.echo(f"🤖 Provider: {provider_name.upper()}")
        
        # Initialize GitHub analyzer and generate basic manifest
        analyzer = GitHubAnalyzer(config_path=config)
        click.echo("📋 Generating file inventory...")
        manifest = analyzer.generate_manifest(repository_url)
        
        # Initialize token analyzer
        from src.token_analyzer import TokenAnalyzer
        token_analyzer = TokenAnalyzer(config_data, provider=provider_name)
        
        # Get cost preview
        click.echo(f"🔍 Analyzing sample of {sample_size} files...")
        cost_preview = token_analyzer.get_cost_preview(manifest, sample_size=sample_size)
        
        # Display detailed cost preview
        click.echo(f"\n📊 Cost Analysis Results:")
        click.echo(f"🏛️  Repository: {manifest.repository.url}")
        click.echo(f"📁 Total files found: {cost_preview['total_files']}")
        click.echo(f"🔬 Sample analyzed: {cost_preview['sample_analyzed']} files")
        click.echo(f"🤖 Provider: {cost_preview['provider'].upper()}")
        click.echo(f"🧠 Model: {cost_preview['model']}")
        
        if cost_preview.get('error'):
            click.echo(f"⚠️  Error: {cost_preview['error']}")
            return
        
        if cost_preview['estimated_total_cost'] > 0:
            click.echo(f"\n💵 Cost Estimation:")
            click.echo(f"   Estimated total: ${cost_preview['estimated_total_cost']:.4f} USD")
            click.echo(f"   Cost per file: ${cost_preview['estimated_total_cost']/cost_preview['total_files']:.4f} USD")
            click.echo(f"📊 Token Estimation:")
            click.echo(f"   Average per file: {cost_preview.get('avg_tokens_per_file', 0):.0f} tokens")
            click.echo(f"   Total estimated: {cost_preview.get('estimated_total_tokens', 0):,.0f} tokens")
            click.echo(f"📈 Confidence: {cost_preview['confidence']}")
            
            # Show pricing details
            pricing = cost_preview.get('pricing', {})
            if pricing:
                click.echo(f"\n💸 Pricing Structure:")
                click.echo(f"   Input: ${pricing.get('input_per_1k', 0)*1000:.3f} per 1M tokens")
                click.echo(f"   Output: ${pricing.get('output_per_1k', 0)*1000:.3f} per 1M tokens")
            
            # Cost categories
            if cost_preview['estimated_total_cost'] > 5.0:
                click.echo(f"\n🚨 VERY HIGH COST: Consider using --provider openai for lower costs")
            elif cost_preview['estimated_total_cost'] > 1.0:
                click.echo(f"\n⚠️  HIGH COST: Review if analysis is necessary")
            elif cost_preview['estimated_total_cost'] > 0.10:
                click.echo(f"\n⚠️  Moderate cost: Proceed with caution")
            else:
                click.echo(f"\n✅ Low cost: Safe to proceed")
                
            # Provide run command
            click.echo(f"\n🚀 To run the analysis:")
            click.echo(f"   python cli.py analyze {repository_url} --phase 2.5 --provider {provider_name}")
            
        else:
            click.echo(f"\nℹ️  No costs estimated (no supported files found or analysis error)")
        
    except Exception as e:
        click.echo(f"❌ Error generating cost preview: {str(e)}")


@cli.command()
@click.argument('manifest_path')
def show(manifest_path):
    """Display information from an existing manifest file"""
    try:
        analyzer = GitHubAnalyzer()
        manifest = analyzer.load_manifest(manifest_path)
        
        click.echo(f"📄 Manifest: {manifest_path}")
        click.echo(f"🏛️  Repository: {manifest.repository.url}")
        click.echo(f"🌿 Default branch: {manifest.repository.default_branch}")
        click.echo(f"📝 Commit SHA: {manifest.repository.commit_sha}")
        click.echo(f"⏰ Analysis time: {manifest.repository.analysis_timestamp}")
        click.echo(f"📁 Total files: {len(manifest.files)}")
        
        # Check if this is a Phase 2 manifest (has LLM analysis)
        llm_analyzed_files = sum(1 for f in manifest.files if hasattr(f, 'purpose') and f.purpose)
        
        if llm_analyzed_files > 0:
            click.echo(f"🧠 LLM analyzed files: {llm_analyzed_files}")
            
            # Show purpose categories
            categories = {}
            security_levels = {}
            
            for file_info in manifest.files:
                if hasattr(file_info, 'purpose') and file_info.purpose:
                    # Get category from metadata
                    llm_metadata = getattr(file_info, 'llm_metadata', {})
                    category = llm_metadata.get('category', 'other')
                    security = llm_metadata.get('security_relevance', 'low')
                    
                    categories[category] = categories.get(category, 0) + 1
                    security_levels[security] = security_levels.get(security, 0) + 1
            
            click.echo("\n📋 Purpose categories:")
            for category, count in sorted(categories.items()):
                click.echo(f"  {category}: {count} files")
            
            click.echo("\n🔒 Security relevance:")
            for level, count in sorted(security_levels.items()):
                click.echo(f"  {level}: {count} files")
        
        # Show file list with purposes if available
        click.echo("\n📋 Files:")
        for file_info in manifest.files[:20]:  # Show first 20 files
            size_kb = file_info.size / 1024
            
            # Check if file has LLM analysis
            if hasattr(file_info, 'purpose') and file_info.purpose:
                llm_metadata = getattr(file_info, 'llm_metadata', {})
                category = llm_metadata.get('category', 'other')
                confidence = getattr(file_info, 'confidence_score', 0.0)
                click.echo(f"  {file_info.path} ({size_kb:.1f} KB) - {category} ({confidence:.2f})")
            else:
                click.echo(f"  {file_info.path} ({size_kb:.1f} KB)")
        
        if len(manifest.files) > 20:
            click.echo(f"  ... and {len(manifest.files) - 20} more files")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--provider', type=click.Choice(['openai', 'bedrock']), default=None, 
              help='LLM provider to test (defaults to config setting)')
def test_llm(config, provider):
    """Test multi-provider LLM connection and analysis"""
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        from src.multi_llm_analyzer import MultiProviderLLMAnalyzer
        
        # If no provider specified, test both
        providers_to_test = [provider] if provider else ['openai', 'bedrock']
        
        for test_provider in providers_to_test:
            try:
                click.echo(f"\n🧠 Testing {test_provider.upper()} LLM provider...")
                
                # Initialize analyzer
                llm_analyzer = MultiProviderLLMAnalyzer(config_data, provider=test_provider)
                
                # Test connection
                if llm_analyzer.test_connection():
                    click.echo(f"✅ {test_provider.upper()} connection successful!")
                    
                    # Test simple analysis
                    from src.github_analyzer import FileInfo
                    test_file = FileInfo(
                        path="test.py",
                        blob_sha="test",
                        size=100,
                        extension=".py"
                    )
                    
                    test_content = """
def hello_world():
    print("Hello, World!")
    return "success"

if __name__ == "__main__":
    hello_world()
"""
                    
                    click.echo(f"🔍 Testing file analysis with {test_provider.upper()}...")
                    response = llm_analyzer.analyze_file_purpose(test_file, test_content)
                    
                    click.echo(f"📋 Analysis Result:")
                    click.echo(f"   Purpose: {response.purpose}")
                    click.echo(f"   Category: {response.category}")
                    click.echo(f"   Confidence: {response.confidence:.2f}")
                    click.echo(f"   Security: {response.security_relevance}")
                    click.echo(f"   Provider: {response.provider}")
                    click.echo(f"   Model: {response.model}")
                    
                else:
                    click.echo(f"❌ {test_provider.upper()} connection failed!")
                    
            except Exception as e:
                click.echo(f"❌ {test_provider.upper()} test failed: {str(e)}")
        
    except FileNotFoundError:
        click.echo(f"❌ Configuration file not found: {config}")
    except Exception as e:
        click.echo(f"❌ Test failed: {str(e)}")


@cli.command()
@click.option('--aws-profile', default='bedrock-dev', help='AWS profile for Bedrock access')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def test_bedrock(aws_profile, config):
    """Test AWS Bedrock LLM connection (legacy command)"""
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        click.echo("🧠 Testing Bedrock LLM connection...")
        llm_analyzer = LLMAnalyzer(config_data, aws_profile=aws_profile)
        
        click.echo("✅ Bedrock LLM connection successful!")
        click.echo(f"🏗️  AWS Profile: {aws_profile}")
        click.echo(f"🌍 Region: {llm_analyzer.region}")
        click.echo(f"🤖 Model: {llm_analyzer.model_id}")
        
    except Exception as e:
        click.echo(f"❌ Bedrock LLM connection failed: {str(e)}", err=True)
        sys.exit(1)
@cli.command()
def test_connection():
    """Test GitHub API connection"""
    try:
        analyzer = GitHubAnalyzer()
        user = analyzer.github.get_user()
        
        click.echo("✅ GitHub connection successful!")
        click.echo(f"👤 Authenticated as: {user.login}")
        
        try:
            rate_limit = analyzer.github.get_rate_limit()
            remaining = rate_limit.core.remaining if hasattr(rate_limit, 'core') else 'N/A'
            click.echo(f"📊 Rate limit remaining: {remaining}")
        except:
            click.echo("📊 Rate limit info: Available")
        
    except Exception as e:
        click.echo(f"❌ Connection failed: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def test_vulnerability_scanner(config):
    """Test vulnerability scanning tools installation and functionality"""
    try:
        click.echo("🔒 Testing vulnerability scanner...")
        
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        from src.vulnerability_scanner import SecurityToolManager
        
        # Test tool installation
        tool_manager = SecurityToolManager()
        click.echo("🔧 Checking security tools...")
        tool_status = tool_manager.check_and_install_tools()
        
        # Display results
        for tool, status in tool_status.items():
            status_icon = "✅" if status else "❌"
            click.echo(f"{status_icon} {tool}: {'Available' if status else 'Failed to install'}")
        
        if all(tool_status.values()):
            click.echo("\n🎉 All vulnerability scanning tools are ready!")
            click.echo("💡 You can now use --scan-vulnerabilities or --phase 3")
        else:
            missing_tools = [tool for tool, status in tool_status.items() if not status]
            click.echo(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
            click.echo("💡 Try running: pip install semgrep bandit[toml]")
        
    except ImportError as e:
        click.echo(f"❌ Vulnerability scanner module not found: {e}")
        click.echo("💡 Make sure src/vulnerability_scanner.py exists")
    except Exception as e:
        click.echo(f"❌ Test failed: {str(e)}")


@cli.command()
@click.argument('repository_url')
@click.argument('file_path')
@click.option('--output', '-o', help='Output file path (default: stdout)')
def get_file(repository_url, file_path, output):
    """Get content of a specific file from repository"""
    try:
        analyzer = GitHubAnalyzer()
        repo, repo_info = analyzer.get_repository_info(repository_url)
        
        # Find file in repository
        try:
            content_file = repo.get_contents(file_path, ref=repo_info.default_branch)
            content = content_file.decoded_content.decode('utf-8')
            
            if output:
                with open(output, 'w') as f:
                    f.write(content)
                click.echo(f"✅ File content saved to: {output}")
            else:
                click.echo(content)
                
        except Exception as e:
            click.echo(f"❌ File not found: {file_path}", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('manifest_path')
@click.option('--output', '-o', default=None, help='Output token analysis file path (defaults to config default)')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--provider', type=click.Choice(['openai', 'bedrock']), default=None, 
              help='LLM provider for cost calculation (defaults to config setting)')
def analyze_tokens(manifest_path, output, config, provider):
    """Analyze token usage and cost estimation for a manifest (Phase 1.5)"""
    click.echo(f"🔢 Analyzing token usage from: {manifest_path}")
    
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        provider_name = provider or config_data.get('llm', {}).get('default_provider', 'openai')
        click.echo(f"🤖 Using pricing for: {provider_name.upper()}")
        
        # Set default output path if not provided
        if output is None:
            output_config = config_data.get('output', {})
            default_dir = output_config.get('default_dir', '.')
            default_filename = output_config.get('token_analysis', 'token_analysis.json')
            output = os.path.join(default_dir, default_filename)
        
        # Initialize analyzers
        github_analyzer = GitHubAnalyzer()
        token_analyzer = TokenAnalyzer(config_data, provider=provider_name)
        
        # Load manifest
        manifest = github_analyzer.load_manifest(manifest_path)
        
        # Perform token analysis
        click.echo("🔍 Calculating tokens and costs...")
        file_stats, repo_stats = token_analyzer.analyze_repository_tokens(manifest, github_analyzer)
        
        # Save token analysis
        token_analyzer.save_token_analysis(file_stats, repo_stats, output)
        
        # Display summary
        token_analyzer.print_token_summary(repo_stats)
        
        click.echo(f"\n✅ Token analysis complete!")
        click.echo(f"📊 Analysis saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
