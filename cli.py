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
    Phase 2: LLM-enhanced code understanding
    """
    pass


@cli.command()
@click.argument('repository_url')
@click.option('--output', '-o', default='manifest.json', help='Output manifest file path')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
@click.option('--phase', '-p', type=click.Choice(['1', '1.5', '2']), default='1', 
              help='Analysis phase: 1=Basic analysis, 1.5=Token analysis, 2=LLM-enhanced analysis')
@click.option('--aws-profile', default='bedrock-dev', help='AWS profile for Bedrock access (Phase 2 only)')
def analyze(repository_url, output, config, phase, aws_profile):
    """Analyze a GitHub repository and generate a manifest"""
    click.echo(f"🔍 Analyzing repository: {repository_url} (Phase {phase})")
    
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Initialize GitHub analyzer
        analyzer = GitHubAnalyzer(config_path=config)
        
        # Generate basic manifest (Phase 1)
        click.echo("📋 Generating base manifest...")
        manifest = analyzer.generate_manifest(repository_url)
        
        if phase == '1.5':
            # Token analysis (Phase 1.5)
            click.echo("🔢 Performing token analysis...")
            token_analyzer = TokenAnalyzer(config_data)
            file_stats, repo_stats = token_analyzer.analyze_repository_tokens(manifest, analyzer)
            
            # Save token analysis
            token_output = output.replace('.json', '_tokens.json')
            token_analyzer.save_token_analysis(file_stats, repo_stats, token_output)
            token_analyzer.print_token_summary(repo_stats)
            click.echo(f"📊 Token analysis saved to: {token_output}")
            
        elif phase == '2':
            # Enhance with LLM analysis (Phase 2)
            click.echo("🧠 Enhancing with LLM analysis...")
            llm_analyzer = LLMAnalyzer(config_data, aws_profile=aws_profile)
            manifest = llm_analyzer.enrich_manifest_with_llm_analysis(manifest, analyzer)
            click.echo("✨ LLM analysis complete!")
        
        # Save manifest
        analyzer.save_manifest(manifest, output)
        
        # Display results
        click.echo("✅ Analysis complete!")
        click.echo(f"📄 Manifest saved to: {output}")
        click.echo(f"🏛️  Repository: {manifest.repository.url}")
        click.echo(f"🌿 Default branch: {manifest.repository.default_branch}")
        click.echo(f"📝 Commit SHA: {manifest.repository.commit_sha}")
        click.echo(f"📁 Files analyzed: {len(manifest.files)}")
        
        if phase == '2':
            # Show LLM analysis summary
            categorized_files = {}
            analyzed_files = 0
            
            for file_info in manifest.files:
                if hasattr(file_info, 'purpose') and file_info.purpose:
                    analyzed_files += 1
                    llm_metadata = getattr(file_info, 'llm_metadata', {})
                    category = llm_metadata.get('category', 'other')
                    categorized_files[category] = categorized_files.get(category, 0) + 1
            
            click.echo(f"\n🧠 LLM Analysis Summary:")
            click.echo(f"📊 Files analyzed: {analyzed_files}/{len(manifest.files)}")
            
            if categorized_files:
                click.echo("\n📋 Purpose categories:")
                for category, count in sorted(categorized_files.items()):
                    click.echo(f"  {category}: {count} files")
        
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
@click.option('--aws-profile', default='bedrock-dev', help='AWS profile for Bedrock access')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def test_llm(aws_profile, config):
    """Test AWS Bedrock LLM connection"""
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        click.echo("🧠 Testing LLM connection...")
        llm_analyzer = LLMAnalyzer(config_data, aws_profile=aws_profile)
        
        click.echo("✅ LLM connection successful!")
        click.echo(f"🏗️  AWS Profile: {aws_profile}")
        click.echo(f"🌍 Region: {llm_analyzer.region}")
        click.echo(f"🤖 Model: {llm_analyzer.model_id}")
        
    except Exception as e:
        click.echo(f"❌ LLM connection failed: {str(e)}", err=True)
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
@click.option('--output', '-o', default='token_analysis.json', help='Output token analysis file path')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def analyze_tokens(manifest_path, output, config):
    """Analyze token usage and cost estimation for a manifest (Phase 1.5)"""
    click.echo(f"🔢 Analyzing token usage from: {manifest_path}")
    
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Initialize analyzers
        github_analyzer = GitHubAnalyzer()
        token_analyzer = TokenAnalyzer(config_data)
        
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
