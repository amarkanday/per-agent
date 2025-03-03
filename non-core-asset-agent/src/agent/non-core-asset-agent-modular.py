import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime

import pandas as pd
import numpy as np

# LangChain imports
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Import specialized agents
from .financial_analysis_agent import FinancialAnalysisAgent
from .operational_assessment_agent import OperationalAssessmentAgent
from .industry_comparison_agent import IndustryComparisonAgent
from .historical_context_agent import HistoricalContextAgent
from .asset_identification_agent import AssetIdentificationAgent

# Import data loaders
from ..data.loaders.sec_loader import SECLoader
from ..data.loaders.web_loader import WebLoader
from ..data.loaders.file_loader import FileLoader
from ..data.loaders.api_connector import FinancialAPIConnector

# Import reporting tools
from ..reporting.report_generator import ReportGenerator

# Import utilities
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class NonCoreAssetAgent:
    """
    Orchestration Agent for identifying non-core assets within a company
    
    This agent coordinates specialized sub-agents to analyze company data across:
    1. Financial Statement Analysis
    2. Operational Assessment
    3. Industry Comparison
    4. Historical Context
    
    Based on these analyses, it identifies and ranks potential non-core assets.
    """
    
    def __init__(self, company_name: str, ticker: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize the Non-Core Asset Agent
        
        Args:
            company_name: Name of the company to analyze
            ticker: Stock ticker symbol if applicable
            config: Configuration settings for the agent
        """
        self.company_name = company_name
        self.ticker = ticker
        self.config = config or {}
        
        # Initialize data repositories
        self.data_sources = {}
        self.analysis_results = {
            "financial_analysis": {},
            "operational_assessment": {},
            "industry_comparison": {},
            "historical_context": {}
        }
        self.non_core_assets = []
        
        # Set up LangChain components
        self._setup_langchain()
        
        # Initialize data loaders
        self._init_data_loaders()
        
        # Initialize specialized agents
        self._init_analysis_agents()
        
        # Initialize reporting
        self.report_generator = ReportGenerator()
        
        # Initialize vector store for document storage
        self.vector_store = None
        
        logger.info(f"Initialized NonCoreAssetAgent for {company_name}")
    
    def _setup_langchain(self):
        """Set up LangChain components"""
        # Initialize language models based on config
        llm_config = self.config.get("llm", {})
        model_name = llm_config.get("model_name", "gpt-4-turbo-preview")
        temperature = llm_config.get("temperature", 0.0)
        api_key = llm_config.get("api_key", os.environ.get("OPENAI_API_KEY"))
        
        if not api_key:
            logger.warning("No API key provided for language model. Some features may be limited.")
        
        # Set up language models
        try:
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=api_key
            )
            logger.info(f"Initialized language model: {model_name}")
        except Exception as e:
            logger.error(f"Error initializing language model: {str(e)}")
            self.llm = None
        
        # Set up embeddings
        try:
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            logger.info("Initialized embeddings model")
        except Exception as e:
            logger.error(f"Error initializing embeddings model: {str(e)}")
            self.embeddings = None
    
    def _init_data_loaders(self):
        """Initialize data loader components"""
        # Initialize data loaders with appropriate config
        self.sec_loader = SECLoader(config=self.config.get("sec_loader", {}))
        self.web_loader = WebLoader(config=self.config.get("web_loader", {}))
        self.file_loader = FileLoader(config=self.config.get("file_loader", {}))
        