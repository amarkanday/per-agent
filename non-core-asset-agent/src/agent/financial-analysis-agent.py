import logging
from typing import Dict, List, Optional, Any
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class FinancialAnalysisAgent:
    """
    Agent responsible for analyzing financial statements to identify non-core assets
    
    This agent focuses on:
    - Assets with low utilization rates
    - Assets with minimal contribution to core revenue
    - Subsidiaries and joint ventures
    - Real estate holdings
    - Intellectual property
    """
    
    def __init__(self, llm=None, config=None):
        """
        Initialize the Financial Analysis Agent
        
        Args:
            llm: Language model for enhanced analysis (optional)
            config: Configuration settings
        """
        self.llm = llm
        self.config = config or {}
        
        # Set up LangChain components if LLM is available
        if self.llm:
            self._setup_chains()
    
    def _setup_chains(self):
        """Set up LangChain chains for analysis"""
        # Create prompt template for financial analysis
        self.financial_prompt = PromptTemplate(
            template="""
            You are a financial analyst specializing in identifying non-core assets. 
            Analyze the following financial statement information for {company_name}.
            
            Financial information:
            {financial_data}
            
            Identify potential non-core assets based on:
            1. Low utilization rates
            2. Minimal contribution to core revenue
            3. Poor alignment with strategic focus
            4. Excessive maintenance or operational costs
            
            For each potential non-core asset, provide:
            - Asset name
            - Asset type
            - Book value (if available)
            - Utilization rate (if applicable)
            - Revenue contribution (if available)
            - A core alignment score from 0.0 (completely non-core) to 1.0 (completely core)
            - Justification for the alignment score
            
            Format your response as a JSON list of assets.
            """,
            input_variables=["company_name", "financial_data"]
        )
        
        # Create chain using the prompt and the LLM
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.financial_prompt,
            output_parser=JsonOutputParser(),
            verbose=self.config.get("verbose", False)
        )
    
    def analyze(self, financial_data: Dict, company_name: str, ticker: Optional[str] = None) -> Dict:
        """
        Analyze financial statements to identify potential non-core assets
        
        Args:
            financial_data: Financial statement data
            company_name: Name of the company
            ticker: Stock ticker symbol (optional)
        
        Returns:
            Dict: Analysis results
        """
        logger.info(f"Analyzing financial statements for {company_name}")
        
        # Initialize results structure
        results = {
            "asset_utilization": {},
            "subsidiaries": {},
            "real_estate": {},
            "ip_assets": {}
        }
        
        try:
            # Enhanced analysis with LLM if available
            if self.llm and hasattr(self, 'analysis_chain'):
                try:
                    # Prepare input for LLM analysis
                    financial_data_str = json.dumps(financial_data, indent=2)
                    
                    # Run analysis chain
                    llm_analysis = self.analysis_chain.run(
                        company_name=company_name,
                        financial_data=financial_data_str
                    )
                    
                    # Parse result if it's a string
                    if isinstance(llm_analysis, str):
                        try:
                            llm_analysis = json.loads(llm_analysis)
                        except:
                            logger.warning("Failed to parse LLM analysis result as JSON")
                            llm_analysis = {"error": "Failed to parse result"}
                    
                    # Combine with traditional analysis
                    traditional_results = self._traditional_analysis(financial_data)
                    results = self._merge_results(llm_analysis, traditional_results)
                    
                    logger.info("Enhanced financial analysis completed with LLM")
                except Exception as e:
                    logger.error(f"Error in LLM-enhanced analysis: {str(e)}")
                    # Fall back to traditional analysis
                    results = self._traditional_analysis(financial_data)
            else:
                # Perform traditional analysis
                results = self._traditional_analysis(financial_data)
            
            logger.info("Financial statement analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in financial statement analysis: {str(e)}")
            raise
    
    def _traditional_analysis(self, financial_data: Dict) -> Dict:
        """
        Perform traditional algorithm-based financial analysis
        
        Args:
            financial_data: Financial statement data
            
        Returns:
            Dict: Analysis results
        """
        results = {
            "asset_utilization": {},
            "subsidiaries": {},
            "real_estate": {},
            "ip_assets": {}
        }
        
        # Analyze asset listings
        results["asset_utilization"] = self._analyze_asset_listings(financial_data)
        
        # Analyze subsidiary listings
        results["subsidiaries"] = self._analyze_subsidiaries(financial_data)
        
        # Analyze real estate holdings
        results["real_estate"] = self._analyze_real_estate(financial_data)
        
        # Analyze intellectual property
        results["ip_assets"] = self._analyze_intellectual_property(financial_data)
        
        return results
    
    def _analyze_asset_listings(self, financial_data: Dict) -> Dict:
        """Analyze detailed asset listings for potential non-core assets"""
        # Implementation would parse balance sheet and notes for detailed asset listings
        # Look for assets with low ROA or utilization rates
        
        # Placeholder for demonstration purposes
        return {
            "low_utilization_assets": [
                {"name": "Manufacturing Plant B", "utilization_rate": 0.35, "book_value": 12500000},
                {"name": "Distribution Center East", "utilization_rate": 0.28, "book_value": 8700000}
            ]
        }
        
    def _analyze_subsidiaries(self, financial_data: Dict) -> Dict:
        """Analyze subsidiary and joint venture listings"""
        # Implementation would extract subsidiary information from financial statements
        # Identify subsidiaries with minimal contribution to core business
        
        # Placeholder for demonstration purposes
        return {
            "non_core_subsidiaries": [
                {"name": "TechSys Solutions", "revenue_contribution": 0.03, "profit_margin": 0.04},
                {"name": "Global Logistics Partners", "revenue_contribution": 0.02, "profit_margin": 0.01}
            ]
        }
        
    def _analyze_real_estate(self, financial_data: Dict) -> Dict:
        """Analyze real estate holdings"""
        # Implementation would identify real estate assets not essential to operations
        
        # Placeholder for demonstration purposes
        return {
            "non_essential_properties": [
                {"location": "Chicago Office Tower Floor 12-14", "book_value": 22000000, "annual_cost": 1200000},
                {"location": "Legacy Manufacturing Campus", "book_value": 18500000, "annual_cost": 950000}
            ]
        }
        
    def _analyze_intellectual_property(self, financial_data: Dict) -> Dict:
        """Analyze intellectual property assets"""
        # Implementation would identify intellectual property with minimal active use
        
        # Placeholder for demonstration purposes
        return {
            "unused_patents": [
                {"patent_id": "US9876543", "description": "Legacy manufacturing process", "book_value": 750000},
                {"patent_id": "US8765432", "description": "Discontinued product technology", "book_value": 1200000}
            ]
        }
    
    def _merge_results(self, llm_results: Any, traditional_results: Dict) -> Dict:
        """
        Merge LLM-based analysis with traditional algorithm-based analysis
        
        Args:
            llm_results: Results from LLM analysis
            traditional_results: Results from traditional analysis
            
        Returns:
            Dict: Merged analysis results
        """
        # Start with traditional results
        merged = traditional_results.copy()
        
        # Add LLM insights
        merged["llm_insights"] = llm_results
        
        # For assets identified by LLM, enhance with additional insights
        if isinstance(llm_results, list):
            # If LLM returns a list of assets
            llm_assets = llm_results
        elif isinstance(llm_results, dict) and "assets" in llm_results:
            # If LLM returns a dict with an assets key
            llm_assets = llm_results["assets"]
        else:
            # No recognizable asset list
            return merged
            
        # Enhance traditional assets with LLM insights
        if "asset_utilization" in traditional_results:
            trad_assets = traditional_results["asset_utilization"].get("low_utilization_assets", [])
            
            # Map of traditional assets by name
            trad_asset_map = {asset["name"]: asset for asset in trad_assets}
            
            for llm_asset in llm_assets:
                asset_name = llm_asset.get("asset_name", "") or llm_asset.get("name", "")
                
                if asset_name in trad_asset_map:
                    trad_asset = trad_asset_map[asset_name]
                    trad_asset["llm_justification"] = llm_asset.get("justification", "")
                    trad_asset["llm_core_alignment"] = llm_asset.get("core_alignment", 0.5)
        
        return merged
