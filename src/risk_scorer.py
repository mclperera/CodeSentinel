"""
Risk Scoring Module for CodeSentinel
Implements configurable rule-based risk assessment for vulnerable files
"""

import yaml
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add parent directory to path for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github_analyzer import FileInfo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RiskAssessment:
    """Data class for risk assessment results"""
    risk_score: float
    priority: str
    sla_hours: Optional[int]
    vulnerability_count: int
    category: str
    security_relevance: str
    component_scores: Dict[str, float]
    reasoning: Optional[str] = None


class RiskScoringEngine:
    """Configurable risk scoring engine for vulnerability assessment"""
    
    def __init__(self, config_path: str = "risk_scoring_config.yaml"):
        """Initialize risk scoring engine with configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        logger.info(f"Risk scoring engine initialized with config: {config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load risk scoring configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.debug(f"Loaded risk scoring configuration: {self.config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Risk scoring config file {self.config_path} not found, using defaults")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing risk scoring config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide default configuration if config file is not available"""
        return {
            'vulnerability_severity_scores': {
                'critical': 10, 'high': 7, 'medium': 4, 'low': 1
            },
            'file_category_scores': {
                'authentication': 10, 'api': 8, 'data-processing': 7,
                'config': 6, 'frontend': 4, 'build': 3, 'test': 2,
                'documentation': 1, 'other': 3
            },
            'security_relevance_scores': {
                'high': 10, 'medium': 5, 'low': 2
            },
            'risk_component_weights': {
                'vulnerability_severity': 0.40,
                'file_category': 0.35,
                'security_relevance': 0.25
            },
            'priority_thresholds': {
                'critical': 8.0, 'high': 6.0, 'medium': 4.0, 'low': 2.0
            },
            'sla_hours': {
                'critical': 4, 'high': 24, 'medium': 72, 'low': 168, 'info': None
            },
            'vulnerability_count_settings': {
                'enabled': True, 'base_multiplier': 0.1, 'max_multiplier': 1.5,
                'critical_high_boost': 1.0
            }
        }
    
    def calculate_vulnerability_severity_score(self, vulnerabilities: List[Dict]) -> float:
        """Calculate vulnerability severity component score"""
        if not vulnerabilities:
            return 0.0
        
        severity_scores = self.config['vulnerability_severity_scores']
        total_score = sum(severity_scores.get(v.get('severity', 'low'), 1) 
                         for v in vulnerabilities)
        
        # Average score per vulnerability
        avg_score = total_score / len(vulnerabilities)
        
        return avg_score
    
    def calculate_category_score(self, file_info: FileInfo) -> float:
        """Calculate file category component score"""
        llm_metadata = file_info.llm_metadata or {}
        category = llm_metadata.get('category', 'other')
        
        category_scores = self.config['file_category_scores']
        return category_scores.get(category, 3)  # Default to 3 if category not found
    
    def calculate_security_relevance_score(self, file_info: FileInfo) -> float:
        """Calculate security relevance component score"""
        llm_metadata = file_info.llm_metadata or {}
        security_relevance = llm_metadata.get('security_relevance', 'low')
        
        relevance_scores = self.config['security_relevance_scores']
        return relevance_scores.get(security_relevance, 2)  # Default to 2 if not found
    
    def apply_vulnerability_count_modifiers(self, base_score: float, vulnerabilities: List[Dict]) -> float:
        """Apply vulnerability count-based modifiers"""
        count_settings = self.config.get('vulnerability_count_settings', {})
        
        if not count_settings.get('enabled', True):
            return base_score
        
        vuln_count = len(vulnerabilities)
        if vuln_count <= 1:
            return base_score
        
        # Count multiplier
        base_multiplier = count_settings.get('base_multiplier', 0.1)
        max_multiplier = count_settings.get('max_multiplier', 1.5)
        count_multiplier = min(1.0 + (vuln_count - 1) * base_multiplier, max_multiplier)
        
        # Critical/High vulnerability boost
        critical_high_boost = count_settings.get('critical_high_boost', 1.0)
        critical_high_count = sum(1 for v in vulnerabilities 
                                 if v.get('severity') in ['critical', 'high'])
        
        boost = critical_high_boost if critical_high_count >= 2 else 0
        
        modified_score = (base_score * count_multiplier) + boost
        return min(modified_score, 10.0)  # Cap at 10.0
    
    def get_priority_level(self, risk_score: float) -> str:
        """Determine priority level based on risk score"""
        thresholds = self.config['priority_thresholds']
        
        if risk_score >= thresholds.get('critical', 8.0):
            return 'CRITICAL'
        elif risk_score >= thresholds.get('high', 6.0):
            return 'HIGH'
        elif risk_score >= thresholds.get('medium', 4.0):
            return 'MEDIUM'
        elif risk_score >= thresholds.get('low', 2.0):
            return 'LOW'
        else:
            return 'INFO'
    
    def get_sla_hours(self, priority: str) -> Optional[int]:
        """Get SLA hours for a given priority level"""
        sla_hours = self.config['sla_hours']
        return sla_hours.get(priority.lower(), None)
    
    def calculate_risk_assessment(self, file_info: FileInfo) -> Optional[RiskAssessment]:
        """
        Calculate comprehensive risk assessment for a file with vulnerabilities
        
        Args:
            file_info: FileInfo object containing vulnerability and LLM data
            
        Returns:
            RiskAssessment object or None if no vulnerabilities found
        """
        vulnerabilities = file_info.vulnerabilities or []
        if not vulnerabilities:
            logger.debug(f"No vulnerabilities found for {file_info.path}, skipping risk assessment")
            return None
        
        # Calculate component scores
        vuln_severity_score = self.calculate_vulnerability_severity_score(vulnerabilities)
        category_score = self.calculate_category_score(file_info)
        relevance_score = self.calculate_security_relevance_score(file_info)
        
        # Apply component weights
        weights = self.config['risk_component_weights']
        base_risk_score = (
            vuln_severity_score * weights.get('vulnerability_severity', 0.40) +
            category_score * weights.get('file_category', 0.35) +
            relevance_score * weights.get('security_relevance', 0.25)
        )
        
        # Apply vulnerability count modifiers
        final_risk_score = self.apply_vulnerability_count_modifiers(base_risk_score, vulnerabilities)
        final_risk_score = round(final_risk_score, 2)
        
        # Determine priority and SLA
        priority = self.get_priority_level(final_risk_score)
        sla_hours = self.get_sla_hours(priority)
        
        # Extract metadata
        llm_metadata = file_info.llm_metadata or {}
        category = llm_metadata.get('category', 'other')
        security_relevance = llm_metadata.get('security_relevance', 'low')
        
        # Create component scores breakdown
        component_scores = {
            'vulnerability_severity': round(vuln_severity_score, 2),
            'file_category': round(category_score, 2),
            'security_relevance': round(relevance_score, 2),
            'base_score': round(base_risk_score, 2),
            'final_score': final_risk_score
        }
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            file_info, vulnerabilities, category, security_relevance, priority
        )
        
        logger.debug(f"Risk assessment for {file_info.path}: {final_risk_score} ({priority})")
        
        return RiskAssessment(
            risk_score=final_risk_score,
            priority=priority,
            sla_hours=sla_hours,
            vulnerability_count=len(vulnerabilities),
            category=category,
            security_relevance=security_relevance,
            component_scores=component_scores,
            reasoning=reasoning
        )
    
    def _generate_reasoning(self, file_info: FileInfo, vulnerabilities: List[Dict], 
                          category: str, security_relevance: str, priority: str) -> str:
        """Generate human-readable reasoning for the risk assessment"""
        
        vuln_count = len(vulnerabilities)
        severity_counts = {}
        for v in vulnerabilities:
            severity = v.get('severity', 'low')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Build reasoning components
        reasons = []
        
        # Vulnerability summary
        if severity_counts:
            severity_summary = ", ".join([f"{count} {severity}" 
                                        for severity, count in severity_counts.items()])
            reasons.append(f"{vuln_count} vulnerabilities found: {severity_summary}")
        
        # Category impact
        if category in ['authentication', 'api', 'data-processing']:
            reasons.append(f"High-impact {category} file")
        elif category in ['config']:
            reasons.append(f"System configuration file")
        
        # Security relevance
        if security_relevance == 'high':
            reasons.append("LLM assessed as high security relevance")
        elif security_relevance == 'medium':
            reasons.append("LLM assessed as medium security relevance")
        
        return "; ".join(reasons)
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config = self._load_config()
        logger.info("Risk scoring configuration reloaded")


# Convenience functions for backward compatibility
def calculate_simple_risk_score(file_info: FileInfo, config_path: str = "risk_scoring_config.yaml") -> float:
    """Calculate risk score using default configuration"""
    engine = RiskScoringEngine(config_path)
    assessment = engine.calculate_risk_assessment(file_info)
    return assessment.risk_score if assessment else 0.0


def get_risk_priority(risk_score: float, config_path: str = "risk_scoring_config.yaml") -> str:
    """Get priority level for a given risk score"""
    engine = RiskScoringEngine(config_path)
    return engine.get_priority_level(risk_score)


def get_sla_hours(priority: str, config_path: str = "risk_scoring_config.yaml") -> Optional[int]:
    """Get SLA hours for a given priority level"""
    engine = RiskScoringEngine(config_path)
    return engine.get_sla_hours(priority)


if __name__ == "__main__":
    # Test the risk scoring engine
    print("Testing Risk Scoring Engine...")
    
    # Initialize engine
    engine = RiskScoringEngine()
    
    # Test configuration loading
    print(f"Loaded config with {len(engine.config)} sections")
    print(f"Priority thresholds: {engine.config['priority_thresholds']}")
    
    print("Risk scoring engine test completed!")
