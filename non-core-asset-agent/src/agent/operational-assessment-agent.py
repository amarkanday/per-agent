import logging
from typing import Dict, List, Optional, Any
import json

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class OperationalAssessmentAgent:
    """
    Agent responsible for assessing operational alignment of assets with core revenue streams
    
    This agent focuses on:
    - Underutilized manufacturing facilities
    - Legacy equipment
    - Excess warehouse/distribution space
    - Non-strategic investments
    - Unused patents/technologies
    """
    
    def __init__(self, llm=None, config=None):
        """
        Initialize the Operational Assessment Agent
        
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
        # Create prompt template for operational analysis
        self.operational_prompt = PromptTemplate(
            template="""
            You are an operations analyst specializing in identifying non-core assets. 
            Analyze the following operational data for {company_name}.
            
            Operational information:
            {operational_data}
            
            Identify operational assets that may be non-core based on:
            1. Low utilization of manufacturing facilities
            2. Legacy equipment from discontinued product lines
            3. Excess warehouse or distribution capacity
            4. Non-strategic investments in other companies
            5. Underused technologies or patents
            
            For each potential non-core operational asset, provide:
            - Asset name
            - Asset type (facility, equipment, warehouse, etc.)
            - Current utilization rate if available
            - Revenue contribution if available
            - Annual maintenance cost if available
            - A core alignment score from 0.0 (completely non-core) to 1.0 (completely core)
            - Justification for the alignment score
            
            Format your response as a JSON list of operational assets.
            """,
            input_variables=["company_name", "operational_data"]
        )
        
        # Create chain using the prompt and the LLM
        self.assessment_chain = LLMChain(
            llm=self.llm,
            prompt=self.operational_prompt,
            output_parser=JsonOutputParser(),
            verbose=self.config.get("verbose", False)
        )
    
    def assess(self, operational_data: Dict, financial_data: Optional[Dict] = None, company_name: str = "") -> Dict:
        """
        Assess operational alignment of assets with core revenue streams
        
        Args:
            operational_data: Operational data
            financial_data: Financial data (optional, for context)
            company_name: Name of the company
            
        Returns:
            Dict: Assessment results
        """
        logger.info(f"Assessing operational alignment for {company_name}")
        
        # Initialize results structure
        results = {
            "revenue_mapping": {},
            "manufacturing_facilities": {},
            "equipment": {},
            "distribution": {},
            "investments": {},
            "technologies": {}
        }
        
        try:
            # Enhanced assessment with LLM if available
            if self.llm and hasattr(self, 'assessment_chain'):
                try:
                    # Prepare input for LLM assessment
                    operational_data_str = json.dumps(operational_data, indent=2)
                    
                    # Run assessment chain
                    llm_assessment = self.assessment_chain.run(
                        company_name=company_name,
                        operational_data=operational_data_str
                    )
                    
                    # Parse result if it's a string
                    if isinstance(llm_assessment, str):
                        try:
                            llm_assessment = json.loads(llm_assessment)
                        except:
                            logger.warning("Failed to parse LLM assessment result as JSON")
                            llm_assessment = {"error": "Failed to parse result"}
                    
                    # Combine with traditional assessment
                    traditional_results = self._traditional_assessment(operational_data, financial_data)
                    results = self._merge_results(llm_assessment, traditional_results)
                    
                    logger.info("Enhanced operational assessment completed with LLM")
                except Exception as e:
                    logger.error(f"Error in LLM-enhanced assessment: {str(e)}")
                    # Fall back to traditional assessment
                    results = self._traditional_assessment(operational_data, financial_data)
            else:
                # Perform traditional assessment
                results = self._traditional_assessment(operational_data, financial_data)
            
            logger.info("Operational assessment completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in operational assessment: {str(e)}")
            raise
    
    def _traditional_assessment(self, operational_data: Dict, financial_data: Optional[Dict] = None) -> Dict:
        """
        Perform traditional algorithm-based operational assessment
        
        Args:
            operational_data: Operational data
            financial_data: Financial data (optional, for context)
            
        Returns:
            Dict: Assessment results
        """
        results = {
            "revenue_mapping": {},
            "manufacturing_facilities": {},
            "equipment": {},
            "distribution": {},
            "investments": {},
            "technologies": {}
        }
        
        # Map assets to revenue streams
        results["revenue_mapping"] = self._map_assets_to_revenue(operational_data)
        
        # Identify underutilized facilities
        results["manufacturing_facilities"] = self._identify_underutilized_facilities(operational_data)
        
        # Identify legacy equipment
        results["equipment"] = self._identify_legacy_equipment(operational_data)
        
        # Identify excess distribution capacity
        results["distribution"] = self._identify_excess_distribution_capacity(operational_data)
        
        # Identify non-strategic investments
        results["investments"] = self._identify_non_strategic_investments(operational_data)
        
        # Identify unused technologies
        results["technologies"] = self._identify_unused_technologies(operational_data)
        
        return results
    
    def _map_assets_to_revenue(self, operational_data: Dict) -> Dict:
        """Map each asset against primary revenue streams"""
        # Implementation would correlate assets with their revenue contribution
        
        # Placeholder for demonstration purposes
        return {
            "assets_by_revenue_contribution": [
                {"asset": "Production Line A", "revenue_contribution": 0.32, "growth_rate": 0.08},
                {"asset": "Production Line B", "revenue_contribution": 0.28, "growth_rate": 0.05},
                {"asset": "Production Line C", "revenue_contribution": 0.03, "growth_rate": -0.12}
            ]
        }
        
    def _identify_underutilized_facilities(self, operational_data: Dict) -> Dict:
        """Identify underutilized manufacturing facilities"""
        # Implementation would analyze facility utilization rates
        
        # Placeholder for demonstration purposes
        return {
            "underutilized_facilities": [
                {"facility": "Plant C", "utilization": 0.35, "annual_maintenance_cost": 2800000},
                {"facility": "Assembly Line 5", "utilization": 0.22, "annual_maintenance_cost": 950000}
            ]
        }
        
    def _identify_legacy_equipment(self, operational_data: Dict) -> Dict:
        """Identify legacy equipment from discontinued product lines"""
        # Implementation would analyze equipment usage and product line status
        
        # Placeholder for demonstration purposes
        return {
            "legacy_equipment": [
                {"equipment": "Stamping Press Model XJ-5", "last_used": "2022-03-15", "book_value": 1250000},
                {"equipment": "Packaging System v2.5", "last_used": "2023-01-10", "book_value": 870000}
            ]
        }
        
    def _identify_excess_distribution_capacity(self, operational_data: Dict) -> Dict:
        """Identify excess warehouse or distribution centers"""
        # Implementation would analyze distribution network efficiency
        
        # Placeholder for demonstration purposes
        return {
            "excess_capacity": [
                {"center": "Northeast Distribution Hub", "utilization": 0.42, "annual_cost": 1850000},
                {"center": "Southern Warehouse B", "utilization": 0.38, "annual_cost": 1420000}
            ]
        }
        
    def _identify_non_strategic_investments(self, operational_data: Dict) -> Dict:
        """Identify non-strategic investments in other companies"""
        # Implementation would analyze investment portfolio alignment with strategy
        
        # Placeholder for demonstration purposes
        return {
            "non_strategic_investments": [
                {"company": "GreenTech Startups Inc.", "ownership": 0.12, "book_value": 3500000, "strategic_alignment": "low"},
                {"company": "Digital Media Group", "ownership": 0.08, "book_value": 2700000, "strategic_alignment": "low"}
            ]
        }
        
    def _identify_unused_technologies(self, operational_data: Dict) -> Dict:
        """Identify patents or technologies from past acquisitions"""
        # Implementation would analyze technology usage from acquisitions
        
        # Placeholder for demonstration purposes
        return {
            "unused_technologies": [
                {"technology": "Quantum Encryption System", "acquisition": "SecureTech (2020)", "current_usage": "minimal"},
                {"technology": "Augmented Reality Platform", "acquisition": "VisionWorks (2021)", "current_usage": "none"}
            ]
        }
    
    def _merge_results(self, llm_results: Any, traditional_results: Dict) -> Dict:
        """
        Merge LLM-based assessment with traditional algorithm-based assessment
        
        Args:
            llm_results: Results from LLM assessment
            traditional_results: Results from traditional assessment
            
        Returns:
            Dict: Merged assessment results
        """
        # Start with traditional results
        merged = traditional_results.copy()
        
        # Add LLM insights
        merged["llm_insights"] = llm_results
        
        # Enhance traditional assets with LLM insights if possible
        # This implementation would depend on the structure of LLM results
        
        return merged
