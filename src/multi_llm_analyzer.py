"""
Multi-Provider LLM Analysis Module for CodeSentinel - Phase 2.5
Support for OpenAI and AWS Bedrock with provider selection
"""

import json
import logging
import time
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod

# OpenAI imports
import openai
from openai import OpenAI

# AWS Bedrock imports
import boto3
from botocore.exceptions import ClientError

from src.github_analyzer import FileInfo, Manifest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Data class for LLM analysis response"""
    purpose: str
    category: str
    confidence: float
    security_relevance: str
    reasoning: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def analyze_file(self, file_path: str, file_content: str, file_extension: str) -> LLMResponse:
        """Analyze a file using the LLM provider"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the LLM provider"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation"""
    
    def __init__(self, config: Dict):
        """Initialize OpenAI provider"""
        self.config = config
        openai_config = config.get('openai', {})
        
        # Get API key from environment or config
        api_key = os.getenv('OPENAPI_KEY') or openai_config.get('api_key', '')
        if api_key.startswith('${') and api_key.endswith('}'):
            # Handle environment variable syntax
            env_var = api_key[2:-1]
            api_key = os.getenv(env_var, '')
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAPI_KEY environment variable.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = openai_config.get('model', 'gpt-4o-mini')
        self.max_tokens = openai_config.get('max_tokens', 1000)
        self.temperature = openai_config.get('temperature', 0.1)
        
        logger.info(f"OpenAI provider initialized with model: {self.model}")
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Test connection"}
                ],
                max_tokens=10,
                temperature=0.1
            )
            logger.info("OpenAI connection test successful")
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {str(e)}")
            return False
    
    def analyze_file(self, file_path: str, file_content: str, file_extension: str) -> LLMResponse:
        """Analyze file using OpenAI GPT"""
        
        prompt = self._create_analysis_prompt(file_path, file_content, file_extension)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior software engineer and security analyst. Analyze code files and provide structured insights about their purpose and security implications."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate required fields
            required_fields = ['purpose', 'category', 'confidence', 'security_relevance']
            if all(field in result for field in required_fields):
                return LLMResponse(
                    purpose=result.get('purpose', 'Unknown purpose'),
                    category=result.get('category', 'other'),
                    confidence=float(result.get('confidence', 0.0)),
                    security_relevance=result.get('security_relevance', 'low'),
                    reasoning=result.get('reasoning', ''),
                    provider='openai',
                    model=self.model
                )
            else:
                logger.warning(f"OpenAI response missing required fields: {result}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
        
        # Return fallback response
        return LLMResponse(
            purpose="Could not analyze file purpose",
            category="other",
            confidence=0.0,
            security_relevance="low",
            reasoning="Analysis failed",
            provider='openai',
            model=self.model
        )
    
    def _create_analysis_prompt(self, file_path: str, file_content: str, file_extension: str) -> str:
        """Create analysis prompt for OpenAI"""
        
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


class BedrockProvider(LLMProvider):
    """AWS Bedrock Claude provider implementation"""
    
    def __init__(self, config: Dict):
        """Initialize Bedrock provider"""
        self.config = config
        bedrock_config = config.get('bedrock', {})
        
        self.region = bedrock_config.get('region', 'us-east-1')
        self.model = bedrock_config.get('model', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        self.max_tokens = bedrock_config.get('max_tokens', 1000)
        self.temperature = bedrock_config.get('temperature', 0.1)
        self.aws_profile = bedrock_config.get('aws_profile', 'bedrock-dev')
        
        # Initialize Bedrock client
        try:
            session = boto3.Session(profile_name=self.aws_profile)
            self.bedrock_client = session.client("bedrock-runtime", region_name=self.region)
            logger.info(f"Bedrock provider initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test AWS Bedrock connection"""
        try:
            test_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": "Test connection"}]}
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model,
                body=json.dumps(test_payload),
                contentType="application/json",
                accept="application/json"
            )
            
            logger.info("Bedrock connection test successful")
            return True
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {str(e)}")
            return False
    
    def analyze_file(self, file_path: str, file_content: str, file_extension: str) -> LLMResponse:
        """Analyze file using AWS Bedrock Claude"""
        
        prompt = self._create_analysis_prompt(file_path, file_content, file_extension)
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
        }
        
        try:
            response = self.bedrock_client.invoke_model(
                modelId=self.model,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            
            result = json.loads(response["body"].read())
            
            if 'content' in result and len(result['content']) > 0:
                content = result['content'][0].get('text', '')
                
                # Extract JSON from response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = content[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                    
                    # Validate required fields
                    required_fields = ['purpose', 'category', 'confidence', 'security_relevance']
                    if all(field in analysis_result for field in required_fields):
                        return LLMResponse(
                            purpose=analysis_result.get('purpose', 'Unknown purpose'),
                            category=analysis_result.get('category', 'other'),
                            confidence=float(analysis_result.get('confidence', 0.0)),
                            security_relevance=analysis_result.get('security_relevance', 'low'),
                            reasoning=analysis_result.get('reasoning', ''),
                            provider='bedrock',
                            model=self.model
                        )
                    
        except Exception as e:
            logger.error(f"Bedrock API error: {str(e)}")
        
        # Return fallback response
        return LLMResponse(
            purpose="Could not analyze file purpose",
            category="other",
            confidence=0.0,
            security_relevance="low",
            reasoning="Analysis failed",
            provider='bedrock',
            model=self.model
        )
    
    def _create_analysis_prompt(self, file_path: str, file_content: str, file_extension: str) -> str:
        """Create analysis prompt for Bedrock"""
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
}}

Provide only the JSON response, no additional text."""


class MultiProviderLLMAnalyzer:
    """Multi-provider LLM analyzer supporting OpenAI and Bedrock"""
    
    def __init__(self, config: Dict, provider: Optional[str] = None):
        """Initialize multi-provider LLM analyzer"""
        self.config = config
        llm_config = config.get('llm', {})
        
        # Determine provider
        self.provider_name = provider or llm_config.get('default_provider', 'openai')
        
        # Initialize selected provider
        if self.provider_name == 'openai':
            self.provider = OpenAIProvider(llm_config)
        elif self.provider_name == 'bedrock':
            self.provider = BedrockProvider(llm_config)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider_name}")
        
        # Analysis configuration
        analysis_config = config.get('analysis', {})
        self.batch_size = analysis_config.get('batch_size', 10)
        self.max_file_size = analysis_config.get('max_file_size', 1048576)
        
        logger.info(f"Multi-provider LLM analyzer initialized with {self.provider_name} provider")
    
    def test_connection(self) -> bool:
        """Test connection to selected LLM provider"""
        return self.provider.test_connection()
    
    def analyze_file_purpose(self, file_info: FileInfo, file_content: str) -> LLMResponse:
        """Analyze a single file's purpose using selected LLM provider"""
        try:
            logger.debug(f"Analyzing file: {file_info.path} with {self.provider_name}")
            response = self.provider.analyze_file(file_info.path, file_content, file_info.extension)
            logger.debug(f"Analysis complete for {file_info.path}: {response.category} (confidence: {response.confidence})")
            return response
        except Exception as e:
            logger.error(f"Error analyzing file {file_info.path}: {str(e)}")
            return LLMResponse(
                purpose="Analysis failed",
                category="other",
                confidence=0.0,
                security_relevance="low",
                reasoning=f"Error: {str(e)}",
                provider=self.provider_name,
                model="unknown"
            )
    
    def batch_analyze_files(self, files_with_content: List[Tuple[FileInfo, str]]) -> List[Tuple[FileInfo, LLMResponse]]:
        """Analyze multiple files in batches"""
        
        results = []
        total_files = len(files_with_content)
        
        logger.info(f"Starting batch analysis of {total_files} files using {self.provider_name}")
        
        for i, (file_info, content) in enumerate(files_with_content, 1):
            logger.info(f"Analyzing file {i}/{total_files}: {file_info.path}")
            
            try:
                llm_response = self.analyze_file_purpose(file_info, content)
                results.append((file_info, llm_response))
                
                # Add delay for rate limiting (OpenAI has better limits than Bedrock)
                if i < total_files:
                    delay = 2 if self.provider_name == 'openai' else 10
                    logger.debug(f"Waiting {delay} seconds before next analysis...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to analyze {file_info.path}: {str(e)}")
                fallback_response = LLMResponse(
                    purpose="Analysis failed",
                    category="other",
                    confidence=0.0,
                    security_relevance="low",
                    reasoning=f"Error: {str(e)}",
                    provider=self.provider_name,
                    model="unknown"
                )
                results.append((file_info, fallback_response))
        
        logger.info(f"Batch analysis complete: {len(results)} files processed with {self.provider_name}")
        return results
    
    def enrich_manifest_with_llm_analysis(self, manifest: Manifest, github_analyzer) -> Manifest:
        """Enrich manifest with LLM analysis results"""
        
        logger.info(f"Starting manifest enrichment with {self.provider_name} LLM analysis")
        
        # Get repository for file content retrieval
        repo, _ = github_analyzer.get_repository_info(manifest.repository.url)
        
        # Prepare files with content for analysis
        files_with_content = []
        
        for file_info in manifest.files:
            try:
                # Get file content using blob SHA
                content = github_analyzer.get_file_content(repo, file_info.blob_sha)
                
                # Skip very large files
                if len(content) > self.max_file_size:
                    logger.warning(f"Skipping large file: {file_info.path} ({len(content)} bytes)")
                    continue
                
                files_with_content.append((file_info, content))
                
            except Exception as e:
                logger.warning(f"Could not retrieve content for {file_info.path}: {str(e)}")
                continue
        
        logger.info(f"Retrieved content for {len(files_with_content)} files")
        
        # Perform batch analysis
        analysis_results = self.batch_analyze_files(files_with_content)
        
        # Update manifest with LLM results
        for file_info, llm_response in analysis_results:
            # Find the corresponding file in manifest and update it
            for manifest_file in manifest.files:
                if manifest_file.path == file_info.path:
                    manifest_file.purpose = llm_response.purpose
                    manifest_file.confidence_score = llm_response.confidence
                    # Store additional LLM metadata
                    manifest_file.llm_metadata = {
                        'category': llm_response.category,
                        'security_relevance': llm_response.security_relevance,
                        'reasoning': llm_response.reasoning,
                        'provider': llm_response.provider,
                        'model': llm_response.model
                    }
                    break
        
        logger.info(f"Manifest enrichment complete using {self.provider_name}")
        return manifest


def main():
    """Test function for multi-provider LLM analyzer"""
    import yaml
    from src.github_analyzer import GitHubAnalyzer
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Test both providers
    providers = ['openai', 'bedrock']
    
    for provider in providers:
        try:
            print(f"\n🧠 Testing {provider.upper()} provider...")
            
            # Initialize analyzer with specific provider
            llm_analyzer = MultiProviderLLMAnalyzer(config, provider=provider)
            
            # Test connection
            if llm_analyzer.test_connection():
                print(f"✅ {provider.upper()} connection successful!")
            else:
                print(f"❌ {provider.upper()} connection failed!")
                continue
            
        except Exception as e:
            print(f"❌ {provider.upper()} initialization failed: {str(e)}")


if __name__ == "__main__":
    main()
