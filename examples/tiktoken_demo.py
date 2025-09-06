#!/usr/bin/env python3
"""
Live demonstration of tiktoken cost calculation
Shows exactly how tokens are counted and costs are calculated
"""

import tiktoken
import json

def demonstrate_tiktoken():
    """Demonstrate tiktoken usage with real examples"""
    
    print("🔍 tiktoken Cost Calculation Demonstration")
    print("=" * 50)
    
    # Initialize encoder
    encoder = tiktoken.get_encoding("cl100k_base")
    
    # AWS Bedrock Claude pricing
    input_price_per_1k = 0.003   # $3 per 1M tokens
    output_price_per_1k = 0.015  # $15 per 1M tokens
    
    # Example 1: Simple Python function
    print("\n📝 Example 1: Simple Python Function")
    print("-" * 30)
    
    simple_code = """def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
    
    # Count tokens
    content_tokens = len(encoder.encode(simple_code))
    print(f"Code content: {repr(simple_code)}")
    print(f"Content tokens: {content_tokens}")
    
    # Show individual tokens
    tokens = encoder.encode(simple_code)
    print(f"First 10 tokens: {tokens[:10]}")
    print(f"Decoded back: {repr(encoder.decode(tokens[:10]))}")
    
    # Example 2: Full prompt construction
    print("\n📝 Example 2: Full Prompt Construction")
    print("-" * 35)
    
    file_path = "src/utils/fibonacci.py"
    file_extension = ".py"
    
    # Our actual prompt template
    prompt_template = """Analyze this code file and identify its primary purpose. Consider:
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
    
    # Build full prompt
    full_prompt = prompt_template.format(
        file_path=file_path,
        file_extension=file_extension,
        file_content=simple_code
    )
    
    # Count prompt tokens
    prompt_tokens = len(encoder.encode(full_prompt))
    
    print(f"Template overhead tokens: {prompt_tokens - content_tokens}")
    print(f"Content tokens: {content_tokens}")  
    print(f"Total prompt tokens: {prompt_tokens}")
    
    # Example 3: Cost calculation
    print("\n💰 Example 3: Cost Calculation")
    print("-" * 25)
    
    # Estimate response tokens (typical JSON response)
    response_tokens = 150
    
    # Calculate costs
    input_cost = (prompt_tokens / 1000) * input_price_per_1k
    output_cost = (response_tokens / 1000) * output_price_per_1k
    total_cost = input_cost + output_cost
    
    print(f"Input tokens: {prompt_tokens}")
    print(f"Output tokens: {response_tokens}")
    print(f"Input cost: ${input_cost:.6f}")
    print(f"Output cost: ${output_cost:.6f}")
    print(f"Total cost: ${total_cost:.6f}")
    
    # Example 4: Different file sizes
    print("\n📊 Example 4: File Size Impact")
    print("-" * 28)
    
    file_sizes = {
        "Small file (50 lines)": "print('hello')\n" * 50,
        "Medium file (200 lines)": "def function():\n    pass\n" * 100,
        "Large file (1000 lines)": "# Complex algorithm\nimport numpy as np\ndef complex_func():\n    return np.array([1,2,3])\n" * 200
    }
    
    for desc, code in file_sizes.items():
        content_tokens = len(encoder.encode(code))
        full_prompt = prompt_template.format(
            file_path="example.py",
            file_extension=".py", 
            file_content=code
        )
        prompt_tokens = len(encoder.encode(full_prompt))
        
        input_cost = (prompt_tokens / 1000) * input_price_per_1k
        output_cost = (response_tokens / 1000) * output_price_per_1k
        total_cost = input_cost + output_cost
        
        print(f"{desc}:")
        print(f"  Content tokens: {content_tokens:,}")
        print(f"  Total prompt tokens: {prompt_tokens:,}")
        print(f"  Cost: ${total_cost:.6f}")
    
    # Example 5: Repository scale
    print("\n🏗️ Example 5: Repository Scale")
    print("-" * 26)
    
    repo_sizes = [
        ("Small repo (10 files)", 10, 800),
        ("Medium repo (100 files)", 100, 1200),
        ("Large repo (1000 files)", 1000, 1500),
        ("Enterprise repo (5000 files)", 5000, 1800)
    ]
    
    for desc, file_count, avg_tokens in repo_sizes:
        total_prompt_tokens = file_count * avg_tokens
        total_response_tokens = file_count * response_tokens
        
        total_input_cost = (total_prompt_tokens / 1000) * input_price_per_1k
        total_output_cost = (total_response_tokens / 1000) * output_price_per_1k
        total_cost = total_input_cost + total_output_cost
        
        print(f"{desc}:")
        print(f"  Total tokens: {total_prompt_tokens + total_response_tokens:,}")
        print(f"  Total cost: ${total_cost:.2f}")
        print(f"  Cost per file: ${total_cost/file_count:.6f}")
    
    # Example 6: Token breakdown
    print("\n🔬 Example 6: Token Breakdown Analysis")
    print("-" * 35)
    
    sample_texts = [
        ("Python keyword", "def function():"),
        ("Variable name", "user_authentication_service"),  
        ("Comment", "# This function handles user authentication"),
        ("String literal", '"Error: Could not connect to database"'),
        ("Import statement", "from typing import List, Dict, Optional"),
        ("Complex expression", "result = np.array([x**2 for x in range(10) if x % 2 == 0])")
    ]
    
    for desc, text in sample_texts:
        tokens = encoder.encode(text)
        chars_per_token = len(text) / len(tokens) if tokens else 0
        print(f"{desc}:")
        print(f"  Text: {text}")
        print(f"  Tokens: {len(tokens)}")
        print(f"  Chars/token: {chars_per_token:.2f}")
        print(f"  Token efficiency: {'High' if chars_per_token > 4 else 'Medium' if chars_per_token > 3 else 'Low'}")

if __name__ == "__main__":
    demonstrate_tiktoken()
