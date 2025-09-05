#!/usr/bin/env python3
"""
CodeSentinel CLI - Phase 1
Command-line interface for GitHub repository analysis
"""

import click
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from github_analyzer import GitHubAnalyzer


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """CodeSentinel - GitHub Repository Risk Analysis Tool"""
    pass


@cli.command()
@click.argument('repository_url')
@click.option('--output', '-o', default='manifest.json', help='Output manifest file path')
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def analyze(repository_url, output, config):
    """Analyze a GitHub repository and generate a manifest (Phase 1)"""
    click.echo(f"🔍 Analyzing repository: {repository_url}")
    
    try:
        # Initialize analyzer
        analyzer = GitHubAnalyzer(config_path=config)
        
        # Generate manifest
        click.echo("📋 Generating manifest...")
        manifest = analyzer.generate_manifest(repository_url)
        
        # Save manifest
        analyzer.save_manifest(manifest, output)
        
        # Display results
        click.echo("✅ Analysis complete!")
        click.echo(f"📄 Manifest saved to: {output}")
        click.echo(f"🏛️  Repository: {manifest.repository.url}")
        click.echo(f"🌿 Default branch: {manifest.repository.default_branch}")
        click.echo(f"📝 Commit SHA: {manifest.repository.commit_sha}")
        click.echo(f"📁 Files analyzed: {len(manifest.files)}")
        
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
        
        # Show file list
        click.echo("\n📋 Files:")
        for file_info in manifest.files[:20]:  # Show first 20 files
            size_kb = file_info.size / 1024
            click.echo(f"  {file_info.path} ({size_kb:.1f} KB)")
        
        if len(manifest.files) > 20:
            click.echo(f"  ... and {len(manifest.files) - 20} more files")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
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


if __name__ == '__main__':
    cli()
