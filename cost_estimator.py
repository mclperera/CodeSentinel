"""
Cost Estimation Tool for Large Repositories
Estimates token usage and costs based on file sizes and types
"""

import json
import statistics
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CostProjection:
    """Cost projection for a repository"""
    total_files: int
    estimated_total_tokens: int
    estimated_total_cost_usd: float
    estimated_analysis_time_hours: float
    file_type_breakdown: Dict[str, Dict]
    cost_by_file_type: Dict[str, float]

class RepositoryCostEstimator:
    """Estimate costs for large repositories without full token analysis"""
    
    def __init__(self):
        # Token estimates per file type based on average file sizes
        self.token_estimates = {
            '.js': 1200,      # Average JavaScript file
            '.jsx': 1400,     # React components (slightly larger)
            '.ts': 1300,      # TypeScript files
            '.tsx': 1500,     # TypeScript React components
            '.py': 1800,      # Python files (tend to be larger)
            '.java': 2200,    # Java files (verbose)
            '.cpp': 2000,     # C++ files
            '.c': 1600,       # C files
            '.h': 800,        # Header files (smaller)
            '.css': 600,      # CSS files (smaller)
            '.html': 500,     # HTML files (markup heavy, fewer tokens)
            '.json': 400,     # JSON config files
            '.yaml': 300,     # YAML config files
            '.yml': 300,      # YAML config files
            '.xml': 500,      # XML files
            '.go': 1400,      # Go files
            '.rb': 1600,      # Ruby files
            '.php': 1500,     # PHP files
            '.cs': 1900,      # C# files
            '.sql': 800,      # SQL files
        }
        
        # Claude pricing (AWS Bedrock)
        self.pricing = {
            'input_tokens_per_1k': 0.003,   # $3 per 1M input tokens
            'output_tokens_per_1k': 0.015   # $15 per 1M output tokens
        }
        
        # Prompt overhead (base prompt + file metadata)
        self.prompt_overhead = 250
        self.response_tokens = 150
        
        # Rate limiting estimates (seconds between requests)
        self.delay_per_request = 20  # Conservative estimate
    
    def estimate_file_tokens(self, file_path: str, file_size: int, extension: str) -> int:
        """Estimate tokens for a single file"""
        
        # Get base estimate for file type
        base_tokens = self.token_estimates.get(extension.lower(), 1000)
        
        # Adjust based on file size (larger files generally have more tokens)
        if file_size > 50000:  # >50KB
            multiplier = 2.0
        elif file_size > 20000:  # >20KB
            multiplier = 1.5
        elif file_size > 5000:   # >5KB
            multiplier = 1.2
        elif file_size < 1000:   # <1KB
            multiplier = 0.5
        else:
            multiplier = 1.0
        
        content_tokens = int(base_tokens * multiplier)
        prompt_tokens = content_tokens + self.prompt_overhead
        total_tokens = prompt_tokens + self.response_tokens
        
        return total_tokens
    
    def estimate_repository_cost(self, manifest_data: Dict) -> CostProjection:
        """Estimate total cost for repository analysis"""
        
        files = manifest_data.get('files', [])
        total_files = len(files)
        
        # Analyze by file type
        file_type_stats = {}
        total_tokens = 0
        total_cost = 0.0
        
        for file_info in files:
            extension = file_info.get('extension', '')
            file_size = file_info.get('size', 0)
            file_path = file_info.get('path', '')
            
            # Estimate tokens for this file
            file_tokens = self.estimate_file_tokens(file_path, file_size, extension)
            
            # Calculate cost for this file
            input_cost = (file_tokens * 0.9 / 1000) * self.pricing['input_tokens_per_1k']  # 90% input
            output_cost = (file_tokens * 0.1 / 1000) * self.pricing['output_tokens_per_1k'] # 10% output
            file_cost = input_cost + output_cost
            
            # Update totals
            total_tokens += file_tokens
            total_cost += file_cost
            
            # Update file type stats
            if extension not in file_type_stats:
                file_type_stats[extension] = {
                    'count': 0,
                    'total_tokens': 0,
                    'total_cost': 0.0,
                    'avg_tokens': 0,
                    'avg_cost': 0.0
                }
            
            stats = file_type_stats[extension]
            stats['count'] += 1
            stats['total_tokens'] += file_tokens
            stats['total_cost'] += file_cost
        
        # Calculate averages for each file type
        for ext, stats in file_type_stats.items():
            if stats['count'] > 0:
                stats['avg_tokens'] = stats['total_tokens'] / stats['count']
                stats['avg_cost'] = stats['total_cost'] / stats['count']
        
        # Calculate analysis time (assuming rate limiting)
        estimated_time_hours = (total_files * self.delay_per_request) / 3600
        
        # Extract cost by file type for summary
        cost_by_file_type = {ext: stats['total_cost'] for ext, stats in file_type_stats.items()}
        
        return CostProjection(
            total_files=total_files,
            estimated_total_tokens=total_tokens,
            estimated_total_cost_usd=total_cost,
            estimated_analysis_time_hours=estimated_time_hours,
            file_type_breakdown=file_type_stats,
            cost_by_file_type=cost_by_file_type
        )
    
    def print_cost_analysis(self, projection: CostProjection, repo_name: str):
        """Print detailed cost analysis"""
        
        print(f"\n💰 Cost Analysis for {repo_name}")
        print(f"=" * 50)
        print(f"📁 Total files: {projection.total_files:,}")
        print(f"🎯 Estimated tokens: {projection.estimated_total_tokens:,}")
        print(f"💵 Estimated cost: ${projection.estimated_total_cost_usd:.2f}")
        print(f"⏱️  Estimated time: {projection.estimated_analysis_time_hours:.1f} hours")
        print(f"💸 Cost per file: ${projection.estimated_total_cost_usd/projection.total_files:.4f}")
        
        print(f"\n📊 Cost Breakdown by File Type:")
        print("-" * 40)
        
        # Sort by cost (highest first)
        sorted_types = sorted(projection.cost_by_file_type.items(), 
                            key=lambda x: x[1], reverse=True)
        
        for ext, cost in sorted_types[:10]:  # Top 10 most expensive
            stats = projection.file_type_breakdown[ext]
            print(f"{ext:>6} | {stats['count']:>4} files | ${cost:>7.2f} | ${stats['avg_cost']:>6.4f}/file")
        
        if len(sorted_types) > 10:
            remaining_cost = sum(cost for _, cost in sorted_types[10:])
            remaining_files = sum(projection.file_type_breakdown[ext]['count'] 
                                for ext, _ in sorted_types[10:])
            print(f"{'Other':>6} | {remaining_files:>4} files | ${remaining_cost:>7.2f} | Various")
        
        print(f"\n⚠️  Rate Limiting Considerations:")
        print(f"   • {projection.total_files:,} requests needed")
        print(f"   • ~{self.delay_per_request}s delay between requests")
        print(f"   • Total time: ~{projection.estimated_analysis_time_hours:.1f} hours")
        print(f"   • Recommendation: Analyze in batches or prioritize high-value files")

def main():
    """Analyze React repository costs"""
    
    # Load React manifest
    with open('react_phase1.json', 'r') as f:
        react_data = json.load(f)
    
    # Create estimator and analyze
    estimator = RepositoryCostEstimator()
    projection = estimator.estimate_repository_cost(react_data)
    
    # Print analysis
    estimator.print_cost_analysis(projection, "React (facebook/react)")
    
    # Save detailed analysis
    output_data = {
        'repository': react_data.get('repository', {}),
        'cost_projection': {
            'total_files': projection.total_files,
            'estimated_total_tokens': projection.estimated_total_tokens,
            'estimated_total_cost_usd': projection.estimated_total_cost_usd,
            'estimated_analysis_time_hours': projection.estimated_analysis_time_hours,
            'cost_per_file': projection.estimated_total_cost_usd / projection.total_files
        },
        'file_type_breakdown': projection.file_type_breakdown,
        'pricing_assumptions': {
            'input_price_per_1k_tokens': estimator.pricing['input_tokens_per_1k'],
            'output_price_per_1k_tokens': estimator.pricing['output_tokens_per_1k'],
            'delay_per_request_seconds': estimator.delay_per_request
        }
    }
    
    # Save to tests/data directory
    import os
    os.makedirs('tests/data', exist_ok=True)
    output_file = 'tests/data/react_cost_analysis.json'
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ Detailed analysis saved to: {output_file}")

if __name__ == "__main__":
    main()
