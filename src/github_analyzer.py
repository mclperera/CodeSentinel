"""
GitHub API integration module for CodeSentinel
Handles repository discovery, branch detection, and blob extraction
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

import requests
from github import Github
from github.Repository import Repository
from github.GitTree import GitTree
from github.ContentFile import ContentFile
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """Data class for file information"""
    path: str
    blob_sha: str
    size: int
    extension: str
    purpose: Optional[str] = None
    confidence_score: Optional[float] = None
    vulnerabilities: List[Dict] = None
    risk_score: Optional[float] = None
    llm_metadata: Optional[Dict] = None
    # New risk assessment fields
    priority: Optional[str] = None
    sla_hours: Optional[int] = None
    vulnerability_score: Optional[float] = None  # Legacy compatibility
    total_vulnerabilities: Optional[int] = None  # Legacy compatibility
    
    def __post_init__(self):
        if self.vulnerabilities is None:
            self.vulnerabilities = []
        if self.llm_metadata is None:
            self.llm_metadata = {}


@dataclass
class RepositoryInfo:
    """Data class for repository information"""
    url: str
    default_branch: str
    commit_sha: str
    analysis_timestamp: str


@dataclass
class Manifest:
    """Data class for the complete manifest"""
    repository: RepositoryInfo
    files: List[FileInfo]


class GitHubAnalyzer:
    """Main class for GitHub repository analysis"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the GitHub analyzer"""
        self.config = self._load_config(config_path)
        self.github_token = os.getenv('GITHUB_TOKEN') or self._extract_token_from_env()
        
        if not self.github_token:
            raise ValueError("GitHub token not found. Please set GITHUB_TOKEN environment variable or add it to .env file")
        
        self.github = Github(self.github_token)
        logger.info("GitHub analyzer initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
                # Replace environment variables in config
                if 'github' in config and 'token' in config['github']:
                    config['github']['token'] = os.path.expandvars(config['github']['token'])
                return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return self._default_config()
    
    def _extract_token_from_env(self) -> Optional[str]:
        """Extract GitHub token from .env file if GITHUB_TOKEN not set"""
        try:
            with open('.env', 'r') as file:
                content = file.read().strip()
                # Simple extraction assuming the token is on the first line
                if content:
                    return content
        except FileNotFoundError:
            logger.warning(".env file not found")
        return None
    
    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'analysis': {
                'file_extensions': ['.py', '.js', '.java', '.go', '.rb', '.php', '.ts', '.jsx', '.tsx'],
                'max_file_size': 1048576,
                'batch_size': 10
            }
        }
    
    def parse_repository_url(self, repo_url: str) -> Tuple[str, str]:
        """Parse repository URL to extract owner and repo name"""
        # Handle different URL formats
        if repo_url.startswith('https://github.com/'):
            path = urlparse(repo_url).path.strip('/')
        elif '/' in repo_url and not repo_url.startswith('http'):
            path = repo_url
        else:
            raise ValueError(f"Invalid repository URL format: {repo_url}")
        
        parts = path.split('/')
        if len(parts) != 2:
            raise ValueError(f"Invalid repository path: {path}")
        
        return parts[0], parts[1]
    
    def get_repository_info(self, repo_url: str) -> Tuple[Repository, RepositoryInfo]:
        """Get repository information and default branch"""
        try:
            owner, repo_name = self.parse_repository_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Get default branch and latest commit
            default_branch = repo.default_branch
            latest_commit = repo.get_branch(default_branch).commit
            
            repo_info = RepositoryInfo(
                url=repo_url,
                default_branch=default_branch,
                commit_sha=latest_commit.sha,
                analysis_timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            logger.info(f"Repository info retrieved: {repo.full_name}, default branch: {default_branch}")
            return repo, repo_info
            
        except Exception as e:
            logger.error(f"Error retrieving repository info: {str(e)}")
            raise
    
    def is_supported_file(self, file_path: str) -> bool:
        """Check if file extension is supported for analysis"""
        supported_extensions = self.config.get('analysis', {}).get('file_extensions', [])
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in supported_extensions
    
    def get_file_inventory(self, repo: Repository, commit_sha: str) -> List[FileInfo]:
        """Extract file inventory from repository using Git Trees API"""
        try:
            # Get the tree for the commit
            tree = repo.get_git_tree(commit_sha, recursive=True)
            files = []
            max_file_size = self.config.get('analysis', {}).get('max_file_size', 1048576)
            
            logger.info(f"Processing {len(tree.tree)} items from repository tree")
            
            for item in tree.tree:
                # Only process blob (file) types
                if item.type == 'blob':
                    file_path = item.path
                    
                    # Check if file is supported and within size limit
                    if self.is_supported_file(file_path) and item.size <= max_file_size:
                        file_extension = os.path.splitext(file_path)[1].lower()
                        
                        file_info = FileInfo(
                            path=file_path,
                            blob_sha=item.sha,
                            size=item.size,
                            extension=file_extension
                        )
                        files.append(file_info)
                        
                        if len(files) % 50 == 0:
                            logger.info(f"Processed {len(files)} supported files...")
            
            logger.info(f"File inventory complete: {len(files)} supported files found")
            return files
            
        except Exception as e:
            logger.error(f"Error extracting file inventory: {str(e)}")
            raise
    
    def generate_manifest(self, repo_url: str) -> Manifest:
        """Generate initial manifest for a repository"""
        try:
            logger.info(f"Starting analysis for repository: {repo_url}")
            
            # Get repository information
            repo, repo_info = self.get_repository_info(repo_url)
            
            # Get file inventory
            files = self.get_file_inventory(repo, repo_info.commit_sha)
            
            # Create manifest
            manifest = Manifest(
                repository=repo_info,
                files=files
            )
            
            logger.info(f"Manifest generated successfully with {len(files)} files")
            return manifest
            
        except Exception as e:
            logger.error(f"Error generating manifest: {str(e)}")
            raise
    
    def save_manifest(self, manifest: Manifest, output_path: str) -> None:
        """Save manifest to JSON file"""
        try:
            # Convert dataclass to dict
            manifest_dict = asdict(manifest)
            
            with open(output_path, 'w') as file:
                json.dump(manifest_dict, file, indent=2)
            
            logger.info(f"Manifest saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving manifest: {str(e)}")
            raise
    
    def load_manifest(self, manifest_path: str) -> Manifest:
        """Load manifest from JSON file"""
        try:
            with open(manifest_path, 'r') as file:
                data = json.load(file)
            
            # Convert dict back to dataclass
            repo_info = RepositoryInfo(**data['repository'])
            files = [FileInfo(**file_data) for file_data in data['files']]
            
            return Manifest(repository=repo_info, files=files)
            
        except Exception as e:
            logger.error(f"Error loading manifest: {str(e)}")
            raise
    
    def get_file_content(self, repo: Repository, blob_sha: str) -> str:
        """Get file content using blob SHA"""
        try:
            blob = repo.get_git_blob(blob_sha)
            # Decode base64 content
            import base64
            content = base64.b64decode(blob.content).decode('utf-8')
            return content
        except Exception as e:
            logger.error(f"Error retrieving file content for blob {blob_sha}: {str(e)}")
            raise


def main():
    """Main function for testing"""
    config_path = "config.yaml"
    analyzer = GitHubAnalyzer(config_path=config_path)
    
    # Example usage
    repo_url = "https://github.com/octocat/Hello-World"
    
    try:
        # Load configuration to get output paths
        import yaml
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        output_config = config_data.get('output', {})
        test_data_dir = output_config.get('test_data_dir', 'tests/data')
        
        # Generate manifest
        manifest = analyzer.generate_manifest(repo_url)
        
        # Save manifest to test data directory
        import os
        os.makedirs(test_data_dir, exist_ok=True)
        output_path = f"{test_data_dir}/manifest_phase1.json"
        analyzer.save_manifest(manifest, output_path)
        
        print(f"Phase 1 complete! Manifest saved to {output_path}")
        print(f"Repository: {manifest.repository.url}")
        print(f"Default branch: {manifest.repository.default_branch}")
        print(f"Commit SHA: {manifest.repository.commit_sha}")
        print(f"Files analyzed: {len(manifest.files)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
