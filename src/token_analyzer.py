"""
Token Analysis Module for CodeSentinel - Phase 1.5
Token counting and cost estimation for LLM analysis
"""

import json
import logging
import tiktoken
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import statistics

from github_analyzer import FileInfo, Manifest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenStats:
    """Token statistics for a file"""
    file_path: str
    file_size_bytes: int
    content_tokens: int
    prompt_tokens: int
    estimated_response_tokens: int
    total_tokens: int
    estimated_cost_usd: float


@dataclass
class RepositoryTokenStats:
    """Aggregated token statistics for entire repository"""
    total_files: int
    analyzed_files: int
    total_content_tokens: int
    total_prompt_tokens: int
    total_response_tokens: int
    total_tokens: int
    estimated_total_cost_usd: float
    average_tokens_per_file: float
    median_tokens_per_file: float
    largest_file_tokens: int
    largest_file_path: str


class TokenAnalyzer:
    """Token analysis and cost estimation for LLM operations"""
    
    def __init__(self, config: Dict):
        """Initialize token analyzer"""
        self.config = config
        
        # Claude pricing (approximate, check AWS for current rates)
        # Claude-3.5-Sonnet pricing on Bedrock (as of 2024)
        self.pricing = {
            'input_tokens_per_1k': 0.003,   # $3 per 1M input tokens
            'output_tokens_per_1k': 0.015   # $15 per 1M output tokens
        }
        
        # Initialize tiktoken encoder for Claude (use cl100k_base as approximation)
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Could not load tiktoken encoder: {e}")
            self.encoder = None
        
        # Analysis prompt template for token counting
        self.prompt_template = self._get_analysis_prompt_template()
        
        logger.info("Token analyzer initialized successfully")
    
    def _get_analysis_prompt_template(self) -> str:
        """Get the prompt template used for analysis"""
        return """Analyze this code file and identify its primary purpose. Consider:
- Main functionality and business logic
- Security implications
- Data handling patterns
- External dependencies
- Framework/library usage patterns
- Architectural role in the application

File: {file_path}
Extension: {file_extension}
Code Content:
```
{file_content}
```

Respond with a JSON object containing:
- "purpose": A brief, clear description of the file's main purpose (max 100 words)
- "category": One of [authentication, data-processing, api, frontend, config, test, build, documentation, other]
- "confidence": A confidence score from 0.0 to 1.0
- "security_relevance": One of [high, medium, low] based on security implications
- "reasoning": Brief explanation of the categorization (max 50 words)

Example response:
{{
  "purpose": "User authentication and session management module",
  "category": "authentication",
  "confidence": 0.95,
  "security_relevance": "high",
  "reasoning": "Handles user credentials, session tokens, and access control"
}}

Provide only the JSON response, no additional text."""
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        if not self.encoder:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4
        
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            logger.warning(f"Error counting tokens: {e}")
            return len(text) // 4
    
    def analyze_file_tokens(self, file_info: FileInfo, file_content: str) -> TokenStats:
        """Analyze token usage for a single file"""
        
        # Count tokens in file content
        content_tokens = self.count_tokens(file_content)
        
        # Create full prompt
        full_prompt = self.prompt_template.format(
            file_path=file_info.path,
            file_extension=file_info.extension,
            file_content=file_content
        )
        
        # Count prompt tokens
        prompt_tokens = self.count_tokens(full_prompt)
        
        # Estimate response tokens (based on typical JSON response size)
        estimated_response_tokens = 150  # Typical response is ~100-200 tokens
        
        # Calculate total tokens
        total_tokens = prompt_tokens + estimated_response_tokens
        
        # Calculate estimated cost
        input_cost = (prompt_tokens / 1000) * self.pricing['input_tokens_per_1k']
        output_cost = (estimated_response_tokens / 1000) * self.pricing['output_tokens_per_1k']
        estimated_cost = input_cost + output_cost
        
        return TokenStats(
            file_path=file_info.path,
            file_size_bytes=file_info.size,
            content_tokens=content_tokens,
            prompt_tokens=prompt_tokens,
            estimated_response_tokens=estimated_response_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost
        )
    
    def analyze_repository_tokens(self, manifest: Manifest, github_analyzer) -> Tuple[List[TokenStats], RepositoryTokenStats]:
        """Analyze token usage for entire repository"""
        
        logger.info("Starting repository token analysis...")
        
        # Get repository for file content retrieval
        repo, _ = github_analyzer.get_repository_info(manifest.repository.url)
        
        file_stats = []
        max_file_size = self.config.get('analysis', {}).get('max_file_size', 1048576)
        
        for file_info in manifest.files:
            try:
                # Get file content
                content = github_analyzer.get_file_content(repo, file_info.blob_sha)
                
                # Skip very large files
                if len(content) > max_file_size:
                    logger.warning(f"Skipping large file: {file_info.path} ({len(content)} bytes)")
                    continue
                
                # Analyze tokens for this file
                stats = self.analyze_file_tokens(file_info, content)
                file_stats.append(stats)
                
                logger.debug(f"Token analysis: {file_info.path} - {stats.total_tokens} tokens (${stats.estimated_cost_usd:.4f})")
                
            except Exception as e:
                logger.warning(f"Could not analyze tokens for {file_info.path}: {str(e)}")
                continue
        
        # Calculate repository-level statistics
        if file_stats:
            total_tokens_list = [s.total_tokens for s in file_stats]
            
            repo_stats = RepositoryTokenStats(
                total_files=len(manifest.files),
                analyzed_files=len(file_stats),
                total_content_tokens=sum(s.content_tokens for s in file_stats),
                total_prompt_tokens=sum(s.prompt_tokens for s in file_stats),
                total_response_tokens=sum(s.estimated_response_tokens for s in file_stats),
                total_tokens=sum(s.total_tokens for s in file_stats),
                estimated_total_cost_usd=sum(s.estimated_cost_usd for s in file_stats),
                average_tokens_per_file=statistics.mean(total_tokens_list),
                median_tokens_per_file=statistics.median(total_tokens_list),
                largest_file_tokens=max(total_tokens_list),
                largest_file_path=max(file_stats, key=lambda x: x.total_tokens).file_path
            )
        else:
            repo_stats = RepositoryTokenStats(
                total_files=len(manifest.files),
                analyzed_files=0,
                total_content_tokens=0,
                total_prompt_tokens=0,
                total_response_tokens=0,
                total_tokens=0,
                estimated_total_cost_usd=0.0,
                average_tokens_per_file=0.0,
                median_tokens_per_file=0.0,
                largest_file_tokens=0,
                largest_file_path=""
            )
        
        logger.info(f"Repository token analysis complete: {len(file_stats)} files analyzed")
        return file_stats, repo_stats
    
    def save_token_analysis(self, file_stats: List[TokenStats], repo_stats: RepositoryTokenStats, 
                           output_path: str) -> None:
        """Save token analysis to JSON file"""
        
        analysis_data = {
            "repository_stats": asdict(repo_stats),
            "file_stats": [asdict(stats) for stats in file_stats],
            "pricing_info": {
                "model": "claude-3.5-sonnet",
                "input_price_per_1k_tokens": self.pricing['input_tokens_per_1k'],
                "output_price_per_1k_tokens": self.pricing['output_tokens_per_1k'],
                "currency": "USD"
            },
            "analysis_metadata": {
                "encoder": "cl100k_base (tiktoken)",
                "note": "Costs are estimates based on AWS Bedrock pricing"
            }
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            logger.info(f"Token analysis saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving token analysis: {str(e)}")
            raise
    
    def print_token_summary(self, repo_stats: RepositoryTokenStats) -> None:
        """Print a summary of token analysis"""
        
        print(f"\n🔢 Token Analysis Summary")
        print(f"📁 Files analyzed: {repo_stats.analyzed_files}/{repo_stats.total_files}")
        print(f"🎯 Total tokens: {repo_stats.total_tokens:,}")
        print(f"📝 Content tokens: {repo_stats.total_content_tokens:,}")
        print(f"💬 Prompt tokens: {repo_stats.total_prompt_tokens:,}")
        print(f"🤖 Response tokens: {repo_stats.total_response_tokens:,}")
        print(f"💰 Estimated cost: ${repo_stats.estimated_total_cost_usd:.4f}")
        print(f"📊 Average tokens/file: {repo_stats.average_tokens_per_file:.0f}")
        print(f"📊 Median tokens/file: {repo_stats.median_tokens_per_file:.0f}")
        print(f"📈 Largest file: {repo_stats.largest_file_path} ({repo_stats.largest_file_tokens:,} tokens)")
        
        # Cost breakdown
        if repo_stats.total_tokens > 0:
            cost_per_file = repo_stats.estimated_total_cost_usd / repo_stats.analyzed_files
            print(f"💵 Average cost/file: ${cost_per_file:.4f}")


def main():
    """Test token analysis functionality"""
    import yaml
    from github_analyzer import GitHubAnalyzer
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize analyzers
    github_analyzer = GitHubAnalyzer()
    token_analyzer = TokenAnalyzer(config)
    
    # Test with existing manifest (check tests/data first, then root)
    import os
    test_manifest_path = "tests/data/patma_phase2.json"
    root_manifest_path = "patma_phase2.json"
    
    manifest_path = test_manifest_path if os.path.exists(test_manifest_path) else root_manifest_path
    
    try:
        # Load configuration
        import yaml
        config_path = "config.yaml"
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        output_config = config_data.get('output', {})
        default_dir = output_config.get('default_dir', '.')
        default_filename = output_config.get('token_analysis', 'token_analysis.json')
        
        # Load manifest
        manifest = github_analyzer.load_manifest(manifest_path)
        
        # Analyze tokens
        file_stats, repo_stats = token_analyzer.analyze_repository_tokens(manifest, github_analyzer)
        
        # Print summary
        token_analyzer.print_token_summary(repo_stats)
        
        # Save analysis to configured directory
        output_path = os.path.join(default_dir, default_filename)
        token_analyzer.save_token_analysis(file_stats, repo_stats, output_path)
        
        print(f"\n✅ Token analysis complete! Saved to {output_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
