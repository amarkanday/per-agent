"""
Configuration settings for the Non-Core Asset Identification Framework.

This module provides configuration defaults and utilities for configuring
the various components of the framework, including:
- Language model settings
- API credentials
- Analysis thresholds
- Data source configurations
- Logging settings
"""

import os
import json
from typing import Dict, Any, Optional

# Default configuration values
DEFAULT_CONFIG = {
    # General settings
    "verbose": False,
    "cache_results": True,
    "cache_dir": "./data/cache",
    
    # Language model settings
    "llm": {
        "enabled": True,
        "model_name": "gpt-4-turbo-preview",  # Alternative: "gpt-3.5-turbo"
        "temperature": 0.0,
        "max_tokens": 2000,
        "api_key": None,  # Will default to OPENAI_API_KEY environment variable
        "retry_attempts": 3,
        "timeout": 60
    },
    
    # Embeddings settings
    "embeddings": {
        "enabled": True,
        "model_name": "text-embedding-ada-002",
        "dimensions": 1536,
        "api_key": None  # Will default to OPENAI_API_KEY environment variable
    },
    
    # Data loaders configuration
    "data_loaders": {
        "sec_loader": {
            "filing_types": ["10-K", "10-Q", "8-K"],
            "max_filings": 5,
            "extract_tables": True,
            "extract_sections": ["Item 1", "Item 1A", "Item 7", "Item 8"]
        },
        "web_loader": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "timeout": 30,
            "max_pages": 10,
            "extract_tables": True,
            "use_selenium": True,
            "wait_time": 5
        },
        "file_loader": {
            "supported_formats": ["csv", "xlsx", "json", "pdf", "txt"],
            "max_file_size_mb": 100
        },
        "api_connector": {
            "retry_attempts": 3,
            "timeout": 30,
            "rate_limit_pause": 1.0  # seconds between requests
        }
    },
    
    # Analysis configurations
    "analysis": {
        "financial_analysis": {
            "low_utilization_threshold": 0.5,  # Assets below this utilization rate are flagged
            "revenue_contribution_threshold": 0.05,  # Assets below this revenue contribution are flagged
            "profit_margin_threshold": 0.1,  # Assets below this profit margin are flagged
            "real_estate_occupancy_threshold": 0.7  # Real estate below this occupancy rate is flagged
        },
        "operational_assessment": {
            "facility_utilization_threshold": 0.6,
            "equipment_age_threshold": 5,  # years
            "warehouse_utilization_threshold": 0.65,
            "technology_usage_threshold": 0.4
        },
        "industry_comparison": {
            "performance_threshold": 0.75,  # Assets below 75% of industry average are flagged
            "significant_deviation": 0.2,  # 20% below industry average is considered significant
            "peer_comparison_count": 5  # Number of peer companies to compare against
        },
        "historical_context": {
            "acquisition_integration_years": 3,  # Years after which acquisitions should be fully integrated
            "market_relevance_threshold": 0.6,  # Assets below this market relevance are flagged
        }
    },
    
    # Identification configurations
    "identification": {
        "confidence_threshold": 0.6,  # Default threshold for classifying as non-core
        "high_confidence_level": 0.8,
        "medium_confidence_level": 0.65,
        "low_confidence_level": 0.5,
        "max_asset_count": 50,  # Maximum number of assets to include in report
        "asset_scoring": {
            "financial_weight": 1.0,
            "operational_weight": 1.0,
            "industry_weight": 1.5,  # Industry comparison given higher weight
            "historical_weight": 1.2
        }
    },
    
    # Reporting configurations
    "reporting": {
        "formats": ["json", "csv", "html"],
        "default_format": "html",
        "visualizations": True,
        "include_details": True,
        "include_summary": True,
        "include_recommendations": True,
        "html_template": "default",  # or "executive", "detailed"
        "color_coding": True
    },
    
    # API keys
    "api_keys": {
        "openai": None,  # Will default to OPENAI_API_KEY environment variable
        "financial_data_api": None,
        "industry_data_api": None,
        "sec_api": None
    },
    
    # Logging settings
    "logging": {
        "level": "INFO",  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
        "file": "./logs/non_core_asset_agent.log",
        "max_file_size_mb": 10,
        "backup_count": 5,
        "console_output": True
    }
}

class AgentConfig:
    """
    Configuration manager for the Non-Core Asset Identification Framework
    
    This class handles loading, validating, and providing access to configuration settings.
    """
    
    def __init__(self, config_path: Optional[str] = None, override_config: Optional[Dict] = None):
        """
        Initialize configuration with optional file path or dictionary override
        
        Args:
            config_path: Path to JSON configuration file (optional)
            override_config: Dictionary of configuration overrides (optional)
        """
        # Start with default configuration
        self.config = DEFAULT_CONFIG.copy()
        
        # Load from file if provided
        if config_path:
            self._load_from_file(config_path)
        
        # Apply environment variable overrides
        self._apply_environment_overrides()
        
        # Apply explicit overrides if provided
        if override_config:
            self._apply_overrides(override_config)
        
        # Validate configuration
        self._validate_config()
    
    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from JSON file
        
        Args:
            config_path: Path to JSON configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                self._apply_overrides(file_config)
        except Exception as e:
            print(f"Warning: Failed to load configuration from {config_path}: {str(e)}")
    
    def _apply_environment_overrides(self) -> None:
        """Apply overrides from environment variables"""
        # Handle API keys
        if not self.config["api_keys"]["openai"] and "OPENAI_API_KEY" in os.environ:
            self.config["api_keys"]["openai"] = os.environ["OPENAI_API_KEY"]
            # Also apply to LLM and embeddings configurations
            self.config["llm"]["api_key"] = os.environ["OPENAI_API_KEY"]
            self.config["embeddings"]["api_key"] = os.environ["OPENAI_API_KEY"]
        
        # Handle other API keys
        if not self.config["api_keys"]["financial_data_api"] and "FINANCIAL_DATA_API_KEY" in os.environ:
            self.config["api_keys"]["financial_data_api"] = os.environ["FINANCIAL_DATA_API_KEY"]
        
        if not self.config["api_keys"]["industry_data_api"] and "INDUSTRY_DATA_API_KEY" in os.environ:
            self.config["api_keys"]["industry_data_api"] = os.environ["INDUSTRY_DATA_API_KEY"]
        
        if not self.config["api_keys"]["sec_api"] and "SEC_API_KEY" in os.environ:
            self.config["api_keys"]["sec_api"] = os.environ["SEC_API_KEY"]
    
    def _apply_overrides(self, override_config: Dict) -> None:
        """
        Apply configuration overrides
        
        Args:
            override_config: Dictionary of configuration overrides
        """
        # Helper function for recursive dictionary update
        def update_dict_recursive(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    update_dict_recursive(target[key], value)
                else:
                    target[key] = value
        
        update_dict_recursive(self.config, override_config)
    
    def _validate_config(self) -> None:
        """Validate configuration settings"""
        # Ensure LLM API key is set if LLM is enabled
        if self.config["llm"]["enabled"] and not self.config["llm"]["api_key"]:
            self.config["llm"]["enabled"] = False
            print("Warning: LLM disabled due to missing API key")
        
        # Ensure embeddings API key is set if embeddings are enabled
        if self.config["embeddings"]["enabled"] and not self.config["embeddings"]["api_key"]:
            self.config["embeddings"]["enabled"] = False
            print("Warning: Embeddings disabled due to missing API key")
        
        # Ensure confidence threshold is valid
        threshold = self.config["identification"]["confidence_threshold"]
        if not (0 <= threshold <= 1):
            self.config["identification"]["confidence_threshold"] = 0.6
            print(f"Warning: Invalid confidence threshold ({threshold}), reset to 0.6")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation path
        
        Args:
            key_path: Dot notation path to configuration value (e.g., "llm.model_name")
            default: Default value to return if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation path
        
        Args:
            key_path: Dot notation path to configuration value (e.g., "llm.model_name")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for i, key in enumerate(keys[:-1]):
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict:
        """
        Get the entire configuration as a dictionary
        
        Returns:
            Dict: Complete configuration dictionary
        """
        return self.config.copy()
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save current configuration to a JSON file
        
        Args:
            file_path: Path to save the configuration file
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {file_path}")
        except Exception as e:
            print(f"Error saving configuration to {file_path}: {str(e)}")
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return json.dumps(self.config, indent=2)
    
    @property
    def llm_enabled(self) -> bool:
        """Check if LLM is enabled and properly configured"""
        return self.config["llm"]["enabled"] and self.config["llm"]["api_key"] is not None
    
    @property
    def embeddings_enabled(self) -> bool:
        """Check if embeddings are enabled and properly configured"""
        return self.config["embeddings"]["enabled"] and self.config["embeddings"]["api_key"] is not None


def load_config(config_path: Optional[str] = None, override_config: Optional[Dict] = None) -> AgentConfig:
    """
    Helper function to load configuration
    
    Args:
        config_path: Path to JSON configuration file (optional)
        override_config: Dictionary of configuration overrides (optional)
        
    Returns:
        AgentConfig: Configuration object
    """
    return AgentConfig(config_path, override_config)
