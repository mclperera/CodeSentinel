#!/usr/bin/env python3
"""
Example script demonstrating the use of the centralized prompts module
This shows how to use different types of prompts and utilities
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from prompts.system_prompts import OPENAI_SYSTEM_PROMPT
from prompts.analysis_prompts import (
    create_file_analysis_prompt, 
    create_bedrock_file_analysis_prompt,
    ANALYSIS_PROMPT_METADATA
)
from prompts.prompt_utils import (
    PromptValidator, 
    PromptCustomizer, 
    truncate_content_if_needed,
    estimate_prompt_tokens
)


def demo_basic_prompts():
    """Demonstrate basic prompt creation"""
    print("🔧 Basic Prompt Creation Demo")
    print("=" * 50)
    
    # Sample file data
    file_path = "src/authentication.py"
    file_extension = ".py"
    file_content = """
def authenticate_user(username, password):
    '''Authenticate user with username and password'''
    # Hash password and compare with stored hash
    hashed = hash_password(password)
    user = database.get_user(username)
    
    if user and user.password_hash == hashed:
        return create_session_token(user.id)
    return None

def hash_password(password):
    '''Hash password using bcrypt'''
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
"""
    
    # Create standard analysis prompt
    print("📝 Standard Analysis Prompt:")
    standard_prompt = create_file_analysis_prompt(file_path, file_content, file_extension)
    print(f"Length: {len(standard_prompt)} chars")
    print(f"Estimated tokens: {estimate_prompt_tokens(standard_prompt)}")
    print()
    
    # Create Bedrock-specific prompt
    print("🤖 Bedrock-Specific Prompt:")
    bedrock_prompt = create_bedrock_file_analysis_prompt(file_path, file_content, file_extension)
    print(f"Length: {len(bedrock_prompt)} chars")
    print(f"Difference from standard: {len(bedrock_prompt) - len(standard_prompt)} chars")
    print()


def demo_system_prompts():
    """Demonstrate system prompt usage"""
    print("🎭 System Prompts Demo")
    print("=" * 50)
    
    print("OpenAI System Prompt:")
    print(f'"{OPENAI_SYSTEM_PROMPT}"')
    print()
    
    # Example of how you'd use it with OpenAI
    print("Example OpenAI message structure:")
    example_messages = [
        {"role": "system", "content": OPENAI_SYSTEM_PROMPT},
        {"role": "user", "content": "Analyze this code..."}
    ]
    print(example_messages)
    print()


def demo_validation():
    """Demonstrate prompt validation utilities"""
    print("✅ Validation Demo") 
    print("=" * 50)
    
    validator = PromptValidator()
    
    # Test file content validation
    print("File content validation:")
    print(f"Valid content: {validator.validate_file_content('print(\"hello\")')}")
    print(f"Empty content: {validator.validate_file_content('')}")
    print(f"Too large content: {validator.validate_file_content('x' * 2000000)}")
    print()
    
    # Test JSON response validation
    print("JSON response validation:")
    valid_json = '{"purpose": "test", "category": "test", "confidence": 0.9, "security_relevance": "low"}'
    invalid_json = '{"purpose": "test"}'
    required_fields = ['purpose', 'category', 'confidence', 'security_relevance']
    
    print(f"Valid JSON: {validator.validate_response_json(valid_json, required_fields)}")
    print(f"Invalid JSON: {validator.validate_response_json(invalid_json, required_fields)}")
    print()
    
    # Test JSON extraction
    print("JSON extraction from response:")
    response_with_extra = "Here's the analysis: " + valid_json + " That's my assessment."
    extracted = validator.extract_json_from_response(response_with_extra)
    print(f"Extracted: {extracted}")
    print()


def demo_customization():
    """Demonstrate prompt customization"""
    print("🎨 Customization Demo")
    print("=" * 50)
    
    customizer = PromptCustomizer()
    
    # Custom categories
    print("Custom categories:")
    custom_cats = ["web", "mobile", "backend", "database", "ai-ml"]
    print(f"Original: {customizer.default_categories}")
    print(f"Custom: {custom_cats}")
    print(f"Formatted: {customizer.customize_categories(custom_cats)}")
    print()
    
    # Specialized prompts
    print("Specialized security-focused prompt:")
    security_prompt = customizer.create_specialized_prompt(
        domain="security",
        file_path="auth.py", 
        file_content="def login(): pass",
        file_extension=".py"
    )
    print(f"Security prompt length: {len(security_prompt)} chars")
    print()


def demo_metadata():
    """Demonstrate prompt metadata"""
    print("📊 Metadata Demo")
    print("=" * 50)
    
    print("Analysis Prompt Metadata:")
    for key, value in ANALYSIS_PROMPT_METADATA.items():
        print(f"  {key}: {value}")
    print()


def demo_utilities():
    """Demonstrate utility functions"""
    print("🛠️ Utilities Demo")
    print("=" * 50)
    
    # Content truncation
    long_content = "x" * 100000
    truncated = truncate_content_if_needed(long_content, max_length=1000)
    print(f"Original length: {len(long_content)}")
    print(f"Truncated length: {len(truncated)}")
    print(f"Truncated preview: {truncated[-100:]}")
    print()


def main():
    """Run all demos"""
    print("🚀 CodeSentinel Prompts Module Demo")
    print("=" * 60)
    print()
    
    try:
        demo_basic_prompts()
        demo_system_prompts()
        demo_validation()
        demo_customization()
        demo_metadata()
        demo_utilities()
        
        print("✅ All demos completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
