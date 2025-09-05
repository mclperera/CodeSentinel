"""
LLM Analysis Module for CodeSentinel - Phase 2
AWS Bedrock integration for intelligent code purpose identification
"""

import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError
import os

from github_analyzer import FileInfo, Manifest

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


class LLMAnalyzer:
    """LLM-powered code analysis using AWS Bedrock"""
    
    def __init__(self, config: Dict, aws_profile: str = "bedrock-dev"):
        """Initialize LLM analyzer with AWS Bedrock"""
        self.config = config
        self.aws_profile = aws_profile
        
        # AWS configuration
        aws_config = config.get('aws', {})
        self.region = aws_config.get('region', 'us-east-1')
        self.model_id = aws_config.get('bedrock_model', 'anthropic.claude-3-5-sonnet-20240620-v1:0')
        
        # Analysis configuration
        analysis_config = config.get('analysis', {})
        self.batch_size = analysis_config.get('batch_size', 10)
        self.max_file_size = analysis_config.get('max_file_size', 1048576)
        
        # Initialize Bedrock client
        self._init_bedrock_client()
        
        logger.info(f"LLM Analyzer initialized with model: {self.model_id}")
    
    def _init_bedrock_client(self):
        """Initialize AWS Bedrock client"""
        try:
            # Use the configured AWS profile
            session = boto3.Session(profile_name=self.aws_profile)
            self.bedrock_client = session.client(
                "bedrock-runtime",
                region_name=self.region
            )
            
            # Test connection
            self._test_bedrock_connection()
            logger.info("AWS Bedrock client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise
    
    def _test_bedrock_connection(self):
        """Test Bedrock connection with a simple query"""
        try:
            test_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": "Test connection"}]}
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(test_payload),
                contentType="application/json",
                accept="application/json"
            )
            
            result = json.loads(response["body"].read())
            logger.info("Bedrock connection test successful")
            
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {str(e)}")
            raise
    
    def _create_analysis_prompt(self, file_path: str, file_content: str, file_extension: str) -> str:
        """Create analysis prompt for file purpose identification"""
        
        prompt = f"""Analyze this code file and identify its primary purpose. Consider:
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
        
        return prompt
    
    def _call_bedrock_llm(self, prompt: str, max_retries: int = 3) -> Dict:
        """Call Bedrock LLM with error handling and retries"""
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.1,  # Low temperature for consistent analysis
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ]
        }
        
        for attempt in range(max_retries):
            try:
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(payload),
                    contentType="application/json",
                    accept="application/json"
                )
                
                result = json.loads(response["body"].read())
                
                # Extract content from Claude response
                if 'content' in result and len(result['content']) > 0:
                    content = result['content'][0].get('text', '')
                    
                    # Parse JSON response
                    try:
                        # Extract JSON from response (in case there's additional text)
                        start_idx = content.find('{')
                        end_idx = content.rfind('}') + 1
                        
                        if start_idx != -1 and end_idx != -1:
                            json_str = content[start_idx:end_idx]
                            analysis_result = json.loads(json_str)
                            
                            # Validate required fields
                            required_fields = ['purpose', 'category', 'confidence', 'security_relevance']
                            if all(field in analysis_result for field in required_fields):
                                return analysis_result
                            else:
                                logger.warning(f"LLM response missing required fields: {analysis_result}")
                                
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse LLM JSON response: {content}")
                
                # If we get here, the response format was unexpected
                logger.warning(f"Unexpected LLM response format: {result}")
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ThrottlingException':
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"AWS Bedrock error: {str(e)}")
                    break
                    
            except Exception as e:
                logger.error(f"Unexpected error calling Bedrock (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                break
        
        # Return fallback response if all attempts failed
        logger.error("All LLM attempts failed, returning fallback response")
        return {
            "purpose": "Could not analyze file purpose",
            "category": "other",
            "confidence": 0.0,
            "security_relevance": "low",
            "reasoning": "Analysis failed"
        }
    
    def analyze_file_purpose(self, file_info: FileInfo, file_content: str) -> LLMResponse:
        """Analyze a single file's purpose using LLM"""
        
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(
                file_info.path, 
                file_content, 
                file_info.extension
            )
            
            # Call LLM
            logger.debug(f"Analyzing file: {file_info.path}")
            result = self._call_bedrock_llm(prompt)
            
            # Create LLMResponse object
            llm_response = LLMResponse(
                purpose=result.get('purpose', 'Unknown purpose'),
                category=result.get('category', 'other'),
                confidence=float(result.get('confidence', 0.0)),
                security_relevance=result.get('security_relevance', 'low'),
                reasoning=result.get('reasoning', '')
            )
            
            logger.debug(f"Analysis complete for {file_info.path}: {llm_response.category} (confidence: {llm_response.confidence})")
            return llm_response
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_info.path}: {str(e)}")
            # Return fallback response
            return LLMResponse(
                purpose="Analysis failed",
                category="other",
                confidence=0.0,
                security_relevance="low",
                reasoning="Error during analysis"
            )
    
    def batch_analyze_files(self, files_with_content: List[Tuple[FileInfo, str]]) -> List[Tuple[FileInfo, LLMResponse]]:
        """Analyze multiple files in batches"""
        
        results = []
        total_files = len(files_with_content)
        
        logger.info(f"Starting batch analysis of {total_files} files")
        
        for i, (file_info, content) in enumerate(files_with_content, 1):
            logger.info(f"Analyzing file {i}/{total_files}: {file_info.path}")
            
            try:
                llm_response = self.analyze_file_purpose(file_info, content)
                results.append((file_info, llm_response))
                
                # Add small delay to avoid rate limiting
                if i % self.batch_size == 0:
                    logger.info(f"Completed batch of {self.batch_size} files, brief pause...")
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Failed to analyze {file_info.path}: {str(e)}")
                # Add fallback response
                fallback_response = LLMResponse(
                    purpose="Analysis failed",
                    category="other",
                    confidence=0.0,
                    security_relevance="low",
                    reasoning=f"Error: {str(e)}"
                )
                results.append((file_info, fallback_response))
        
        logger.info(f"Batch analysis complete: {len(results)} files processed")
        return results
    
    def enrich_manifest_with_llm_analysis(self, manifest: Manifest, github_analyzer) -> Manifest:
        """Enrich manifest with LLM analysis results"""
        
        logger.info("Starting manifest enrichment with LLM analysis")
        
        # Get repository for file content retrieval
        repo, _ = github_analyzer.get_repository_info(manifest.repository.url)
        
        # Prepare files with content for analysis
        files_with_content = []
        
        for file_info in manifest.files:
            try:
                # Get file content using blob SHA
                content = github_analyzer.get_file_content(repo, file_info.blob_sha)
                
                # Skip very large files or binary content
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
                    if not hasattr(manifest_file, 'llm_metadata'):
                        manifest_file.__dict__['llm_metadata'] = {}
                    manifest_file.__dict__['llm_metadata'] = {
                        'category': llm_response.category,
                        'security_relevance': llm_response.security_relevance,
                        'reasoning': llm_response.reasoning
                    }
                    break
        
        logger.info("Manifest enrichment complete")
        return manifest


def main():
    """Test function for LLM analyzer"""
    import yaml
    from github_analyzer import GitHubAnalyzer
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize analyzers
    github_analyzer = GitHubAnalyzer()
    llm_analyzer = LLMAnalyzer(config)
    
    # Test with a small repository
    repo_url = "https://github.com/octocat/Hello-World"
    
    try:
        # Generate base manifest
        manifest = github_analyzer.generate_manifest(repo_url)
        
        # Enrich with LLM analysis
        enriched_manifest = llm_analyzer.enrich_manifest_with_llm_analysis(manifest, github_analyzer)
        
        # Save enriched manifest
        github_analyzer.save_manifest(enriched_manifest, "manifest_phase2.json")
        
        print("Phase 2 LLM analysis complete!")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
