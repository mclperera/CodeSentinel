# CodeSentinel Prompts Module

This directory contains all the LLM prompts used throughout the CodeSentinel application, providing a centralized and organized approach to prompt management.

## Structure

### `system_prompts.py`
Contains system-level prompts that define the role and behavior of different LLM providers:
- OpenAI system prompt for code analysis
- Future system prompts for other providers

### `analysis_prompts.py`
Contains prompts for code file analysis:
- `create_file_analysis_prompt()` - Standard analysis prompt
- `create_bedrock_file_analysis_prompt()` - Bedrock-specific version
- `ANALYSIS_PROMPT_TEMPLATE` - Template for custom prompts
- `ANALYSIS_PROMPT_METADATA` - Metadata about prompt specifications

### `prompt_utils.py`
Utility functions for prompt management:
- `PromptValidator` - Validates inputs and responses
- `PromptCustomizer` - Customizes prompts for different use cases
- Helper functions for content handling and token estimation

## Usage Examples

### Basic File Analysis
```python
from prompts.analysis_prompts import create_file_analysis_prompt

prompt = create_file_analysis_prompt(
    file_path="src/auth.py",
    file_content="def login(username, password): ...",
    file_extension=".py"
)
```

### Using System Prompts
```python
from prompts.system_prompts import OPENAI_SYSTEM_PROMPT

messages = [
    {"role": "system", "content": OPENAI_SYSTEM_PROMPT},
    {"role": "user", "content": analysis_prompt}
]
```

### Custom Prompt Creation
```python
from prompts.prompt_utils import PromptCustomizer

customizer = PromptCustomizer()
security_prompt = customizer.create_specialized_prompt(
    domain="security",
    file_path="auth.py", 
    file_content=content,
    file_extension=".py"
)
```

### Validating Responses
```python
from prompts.prompt_utils import PromptValidator

validator = PromptValidator()
is_valid = validator.validate_response_json(
    response, 
    required_fields=['purpose', 'category', 'confidence', 'security_relevance']
)
```

## Benefits of This Structure

1. **Centralized Management**: All prompts in one location
2. **Version Control**: Easy to track prompt changes and improvements
3. **Reusability**: Shared prompts across different analyzers
4. **Customization**: Easy to create specialized prompts
5. **Validation**: Built-in validation for prompt inputs/outputs
6. **Documentation**: Clear documentation of prompt specifications
7. **Testing**: Easy to test and iterate on prompts

## Prompt Categories

### File Analysis Categories
- `authentication` - Auth and security modules
- `data-processing` - Data manipulation and processing
- `api` - API endpoints and handlers
- `frontend` - UI components and client-side code
- `config` - Configuration files and settings
- `test` - Test files and testing utilities
- `build` - Build scripts and deployment
- `documentation` - Documentation files
- `other` - Everything else

### Security Relevance Levels
- `high` - Direct security implications
- `medium` - Moderate security considerations  
- `low` - Minimal security impact

## Future Enhancements

- Add more specialized domain prompts (performance, architecture, etc.)
- Implement prompt A/B testing framework
- Add multi-language prompt support
- Create prompt optimization tools
- Add prompt performance metrics
