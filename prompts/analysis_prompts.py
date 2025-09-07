"""
Analysis prompts for code file purpose identification
These prompts are used to analyze individual code files and extract their purpose, category, and security relevance
"""

from typing import Dict, Any


def create_file_analysis_prompt(file_path: str, file_content: str, file_extension: str) -> str:
    """
    Create a standardized file analysis prompt for any LLM provider
    
    Args:
        file_path: Path to the file being analyzed
        file_content: Content of the file to analyze
        file_extension: File extension (e.g., .py, .js, .java)
        
    Returns:
        Formatted prompt string ready for LLM consumption
    """
    return f"""Analyze this code file and identify its primary purpose. Consider:
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
}}"""


def create_bedrock_file_analysis_prompt(file_path: str, file_content: str, file_extension: str) -> str:
    """
    Create a Bedrock-specific file analysis prompt
    Bedrock (Claude) requires explicit instruction to provide only JSON response
    
    Args:
        file_path: Path to the file being analyzed
        file_content: Content of the file to analyze
        file_extension: File extension (e.g., .py, .js, .java)
        
    Returns:
        Formatted prompt string for Bedrock/Claude
    """
    base_prompt = create_file_analysis_prompt(file_path, file_content, file_extension)
    return f"{base_prompt}\n\nProvide only the JSON response, no additional text."


# Template for creating custom analysis prompts
ANALYSIS_PROMPT_TEMPLATE = """Analyze this code file and identify its primary purpose. Consider:
- Main functionality and business logic
- Security implications
- Data handling patterns
- External dependencies
- Framework/library usage patterns
- Architectural role in the application

File: {{file_path}}
Extension: {{file_extension}}
Code Content:
```
{{file_content}}
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
}}"""


# Metadata about our analysis prompts
ANALYSIS_PROMPT_METADATA = {
    "version": "1.0",
    "last_updated": "2025-09-07",
    "supported_categories": [
        "authentication",
        "data-processing", 
        "api",
        "frontend",
        "config",
        "test",
        "build",
        "documentation",
        "other"
    ],
    "security_levels": [
        "high",
        "medium", 
        "low"
    ],
    "response_format": "json",
    "max_purpose_length": 100,
    "max_reasoning_length": 50
}
