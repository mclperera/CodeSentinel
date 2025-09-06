#!/usr/bin/env python3
"""
Show real token analysis data from our repository analysis
"""

import json

def show_real_analysis():
    """Display real token analysis results"""
    
    with open('token_analysis.json', 'r') as f:
        data = json.load(f)

    print('🔍 Real Token Analysis from patma Repository:')
    print('=' * 50)

    repo_stats = data['repository_stats']
    print(f'📁 Files analyzed: {repo_stats["analyzed_files"]}')
    print(f'🎯 Total tokens: {repo_stats["total_tokens"]:,}')
    print(f'💰 Total cost: ${repo_stats["estimated_total_cost_usd"]:.4f}')
    print(f'📊 Average tokens/file: {repo_stats["average_tokens_per_file"]:.0f}')

    print(f'\n📋 Individual File Breakdown:')
    print('-' * 60)
    print(f'{"File":<25} {"Content":<8} {"Prompt":<8} {"Total":<8} {"Cost":<10}')
    print('-' * 60)
    
    for file_stat in data['file_stats']:
        filename = file_stat["file_path"].split('/')[-1]  # Just filename
        print(f'{filename:<25} {file_stat["content_tokens"]:<8,} {file_stat["prompt_tokens"]:<8,} {file_stat["total_tokens"]:<8,} ${file_stat["estimated_cost_usd"]:<9.6f}')

    print(f'\n💡 Key Insights:')
    print(f'• Template overhead: ~{repo_stats["total_prompt_tokens"] - repo_stats["total_content_tokens"]:,} tokens ({((repo_stats["total_prompt_tokens"] - repo_stats["total_content_tokens"]) / repo_stats["total_prompt_tokens"] * 100):.1f}%)')
    print(f'• Content efficiency: ~{repo_stats["total_content_tokens"] / repo_stats["total_prompt_tokens"] * 100:.1f}% of prompt is actual code')
    print(f'• Cost per 1000 tokens: ${repo_stats["estimated_total_cost_usd"] / repo_stats["total_tokens"] * 1000:.4f}')

if __name__ == "__main__":
    show_real_analysis()
