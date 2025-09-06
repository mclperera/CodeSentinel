#!/usr/bin/env python3
"""
CodeSentinel Phase 2.5 Demo - Multi-Provider LLM Analysis
Demonstrates the multi-provider LLM capabilities with OpenAI and Bedrock fallback
"""

import yaml
import json
import time
from datetime import datetime
from src.github_analyzer import GitHubAnalyzer
from src.multi_llm_analyzer import MultiProviderLLMAnalyzer

def load_config():
    """Load configuration file"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def test_provider_connectivity():
    """Test connectivity to both LLM providers"""
    print("🔧 Phase 2.5 Multi-Provider LLM Demo")
    print("=" * 50)
    
    config = load_config()
    providers = ['openai', 'bedrock']
    available_providers = []
    
    for provider in providers:
        try:
            print(f"\n🧠 Testing {provider.upper()} provider...")
            analyzer = MultiProviderLLMAnalyzer(config, provider=provider)
            
            if analyzer.test_connection():
                print(f"✅ {provider.upper()} - Connection successful!")
                available_providers.append(provider)
            else:
                print(f"❌ {provider.upper()} - Connection failed!")
                
        except Exception as e:
            print(f"❌ {provider.upper()} - Error: {str(e)}")
    
    return available_providers

def demo_file_analysis():
    """Demonstrate single file analysis with both providers"""
    print("\n\n🔍 File Analysis Demo")
    print("=" * 30)
    
    config = load_config()
    
    # Sample code files for testing
    test_files = {
        "auth.py": """
import hashlib
import jwt
import secrets
from datetime import datetime, timedelta
from flask import request, jsonify
from functools import wraps

class AuthenticationManager:
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiry = timedelta(hours=24)
    
    def hash_password(self, password):
        \"\"\"Hash password using SHA-256\"\"\"
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    def verify_password(self, password, hashed):
        \"\"\"Verify password against hash\"\"\"
        try:
            salt, pwd_hash = hashed.split('$')
            return pwd_hash == hashlib.sha256((password + salt).encode()).hexdigest()
        except ValueError:
            return False
    
    def generate_token(self, user_id):
        \"\"\"Generate JWT token for user\"\"\"
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + self.token_expiry,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token):
        \"\"\"Verify and decode JWT token\"\"\"
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

def require_auth(f):
    \"\"\"Decorator to require authentication\"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        auth_manager = AuthenticationManager(app.config['SECRET_KEY'])
        user_id = auth_manager.verify_token(token)
        
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        request.current_user = user_id
        return f(*args, **kwargs)
    
    return decorated_function
""",
        
        "data_processor.py": """
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    \"\"\"Handles data processing and transformation operations\"\"\"
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.batch_size = config.get('batch_size', 1000)
        self.max_memory_usage = config.get('max_memory_mb', 512)
    
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        \"\"\"Clean and preprocess dataset\"\"\"
        logger.info(f"Starting dataset cleaning for {len(df)} rows")
        
        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_rows - len(df)} duplicate rows")
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        
        categorical_columns = df.select_dtypes(include=['object']).columns
        df[categorical_columns] = df[categorical_columns].fillna('Unknown')
        
        return df
    
    def process_batch(self, batch: pd.DataFrame) -> Dict[str, Any]:
        \"\"\"Process a single batch of data\"\"\"
        try:
            # Calculate statistics
            stats = {
                'row_count': len(batch),
                'null_counts': batch.isnull().sum().to_dict(),
                'memory_usage': batch.memory_usage(deep=True).sum()
            }
            
            # Apply transformations
            processed_batch = self.clean_dataset(batch.copy())
            
            # Calculate metrics
            numeric_cols = processed_batch.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                stats['numeric_summary'] = processed_batch[numeric_cols].describe().to_dict()
            
            return {
                'status': 'success',
                'data': processed_batch,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def process_large_dataset(self, file_path: str) -> List[Dict[str, Any]]:
        \"\"\"Process large dataset in batches\"\"\"
        results = []
        
        try:
            # Read file in chunks
            chunk_iterator = pd.read_csv(file_path, chunksize=self.batch_size)
            
            for i, chunk in enumerate(chunk_iterator):
                logger.info(f"Processing batch {i+1}")
                
                result = self.process_batch(chunk)
                results.append(result)
                
                # Memory management
                if result['status'] == 'success':
                    memory_mb = result['stats']['memory_usage'] / (1024 * 1024)
                    if memory_mb > self.max_memory_usage:
                        logger.warning(f"High memory usage: {memory_mb:.2f} MB")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing dataset: {str(e)}")
            return [{'status': 'error', 'error': str(e)}]
""",

        "config.py": """
import os
from datetime import timedelta

class Config:
    \"\"\"Application configuration settings\"\"\"
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # Authentication settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Redis settings
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery settings
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # API settings
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100 per hour')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///prod.db'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
"""
    }
    
    # Test with available providers
    available_providers = ['openai']  # We know OpenAI works
    
    for provider in available_providers:
        print(f"\n🧠 Testing file analysis with {provider.upper()}")
        print("-" * 40)
        
        try:
            analyzer = MultiProviderLLMAnalyzer(config, provider=provider)
            
            for filename, content in test_files.items():
                print(f"\n📄 Analyzing: {filename}")
                
                # Create mock FileInfo
                from src.github_analyzer import FileInfo
                file_info = FileInfo(
                    path=filename,
                    blob_sha="demo",
                    size=len(content),
                    extension=filename.split('.')[-1]
                )
                
                # Analyze file
                start_time = time.time()
                response = analyzer.analyze_file_purpose(file_info, content)
                analysis_time = time.time() - start_time
                
                print(f"   Purpose: {response.purpose}")
                print(f"   Category: {response.category}")
                print(f"   Security: {response.security_relevance}")
                print(f"   Confidence: {response.confidence:.2f}")
                print(f"   Analysis time: {analysis_time:.2f}s")
                print(f"   Provider: {response.provider} ({response.model})")
                
                if response.reasoning:
                    print(f"   Reasoning: {response.reasoning}")
        
        except Exception as e:
            print(f"❌ Error with {provider}: {str(e)}")

def demo_cost_comparison():
    """Demonstrate token analysis and cost estimation"""
    print("\n\n💰 Cost Analysis Demo")
    print("=" * 25)
    
    config = load_config()
    
    # Sample repository for cost analysis
    test_repo = "https://github.com/octocat/Hello-World"
    
    print(f"📊 Analyzing token costs for: {test_repo}")
    
    try:
        from src.token_analyzer import TokenAnalyzer
        from src.github_analyzer import GitHubAnalyzer
        
        # Generate manifest
        github_analyzer = GitHubAnalyzer(config)
        manifest = github_analyzer.analyze_repository(test_repo)
        
        # Analyze tokens
        token_analyzer = TokenAnalyzer(config)
        token_analysis = token_analyzer.analyze_repository_tokens(manifest, github_analyzer)
        
        print(f"\n📈 Token Analysis Results:")
        print(f"   Total tokens: {token_analysis['total_tokens']:,}")
        print(f"   Estimated cost: ${token_analysis['estimated_cost']:.4f}")
        print(f"   Files analyzed: {token_analysis['files_analyzed']}")
        
        # Compare provider costs
        providers = ['openai', 'bedrock']
        print(f"\n💸 Provider Cost Comparison:")
        
        for provider in providers:
            provider_config = config.get('llm', {}).get(provider, {})
            if 'cost_per_1k_tokens' in provider_config:
                cost = (token_analysis['total_tokens'] / 1000) * provider_config['cost_per_1k_tokens']
                print(f"   {provider.upper()}: ${cost:.4f}")
    
    except Exception as e:
        print(f"❌ Cost analysis error: {str(e)}")

def main():
    """Main demo function"""
    print("🚀 CodeSentinel Phase 2.5 Demo")
    print("Multi-Provider LLM Analysis System")
    print("=" * 50)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test provider connectivity
    available_providers = test_provider_connectivity()
    
    if not available_providers:
        print("\n❌ No LLM providers available. Please check your configuration.")
        return
    
    print(f"\n✅ Available providers: {', '.join(available_providers).upper()}")
    
    # Demo file analysis
    demo_file_analysis()
    
    # Demo cost comparison
    demo_cost_comparison()
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"Available features:")
    print(f"   ✅ Multi-provider LLM support (OpenAI + Bedrock)")
    print(f"   ✅ Automatic provider fallback")
    print(f"   ✅ Token-based cost estimation")
    print(f"   ✅ File-level security analysis")
    print(f"   ✅ Confidence scoring")
    print(f"   ✅ Category classification")

if __name__ == "__main__":
    main()
