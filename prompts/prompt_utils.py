"""
Prompt utilities and helpers
Common functions for prompt management, validation, and customization
"""

from typing import Dict, List, Optional
import re
import json


class PromptValidator:
    """Validates prompt inputs and responses"""
    
    @staticmethod
    def validate_file_content(content: str, max_size: int = 1048576) -> bool:
        """Validate file content for prompt inclusion"""
        if not content or not isinstance(content, str):
            return False
        if len(content) > max_size:
            return False
        return True
    
    @staticmethod
    def validate_response_json(response: str, required_fields: List[str]) -> bool:
        """Validate LLM JSON response format"""
        try:
            data = json.loads(response)
            return all(field in data for field in required_fields)
        except json.JSONDecodeError:
            return False
    
    @staticmethod
    def extract_json_from_response(response: str) -> Optional[Dict]:
        """Extract JSON object from LLM response text"""
        try:
            # Look for JSON object in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        return None


class PromptCustomizer:
    """Customizes prompts for different use cases and providers"""
    
    def __init__(self):
        self.default_categories = [
            "authentication", "data-processing", "api", "frontend", 
            "config", "test", "build", "documentation", "other"
        ]
        self.security_levels = ["high", "medium", "low"]
    
    def customize_categories(self, categories: List[str]) -> str:
        """Customize the category list in prompts"""
        return f"[{', '.join(categories)}]"
    
    def add_custom_instructions(self, base_prompt: str, instructions: str) -> str:
        """Add custom analysis instructions to base prompt"""
        lines = base_prompt.split('\n')
        # Insert custom instructions after the "Consider:" section
        consider_line = next((i for i, line in enumerate(lines) if "Consider:" in line), 0)
        
        if consider_line:
            lines.insert(consider_line + len(self._get_consider_items()) + 1, f"- {instructions}")
        
        return '\n'.join(lines)
    
    def _get_consider_items(self) -> List[str]:
        """Get the default 'Consider:' items"""
        return [
            "- Main functionality and business logic",
            "- Security implications", 
            "- Data handling patterns",
            "- External dependencies",
            "- Framework/library usage patterns",
            "- Architectural role in the application"
        ]
    
    def create_specialized_prompt(self, 
                                domain: str, 
                                file_path: str, 
                                file_content: str, 
                                file_extension: str) -> str:
        """Create domain-specific analysis prompts"""
        
        domain_instructions = {
            "security": "Pay special attention to authentication, authorization, encryption, input validation, and potential vulnerabilities.",
            "performance": "Focus on performance implications, optimization opportunities, and resource usage patterns.",
            "architecture": "Analyze architectural patterns, design principles, and system integration points.",
            "testing": "Examine test coverage, testing strategies, and quality assurance practices."
        }
        
        base_instruction = domain_instructions.get(domain, "")
        
        return f"""Analyze this code file with a focus on {domain} aspects. {base_instruction}

File: {file_path}
Extension: {file_extension}
Code Content:
```
{file_content}
```

Provide detailed analysis considering {domain} implications and best practices."""


def truncate_content_if_needed(content: str, max_length: int = 50000) -> str:
    """Truncate file content if it's too long for prompt"""
    if len(content) <= max_length:
        return content
    
    # Truncate and add indication
    truncated = content[:max_length]
    return f"{truncated}\n\n... [Content truncated due to length - showing first {max_length} characters]"


def sanitize_file_path(file_path: str) -> str:
    """Sanitize file path for safe inclusion in prompts"""
    # Remove any potentially problematic characters
    sanitized = re.sub(r'[<>:"|?*]', '_', file_path)
    return sanitized


def estimate_prompt_tokens(prompt: str) -> int:
    """Rough estimation of token count for prompt planning"""
    # Very rough approximation: ~4 characters per token for English text
    return len(prompt) // 4
