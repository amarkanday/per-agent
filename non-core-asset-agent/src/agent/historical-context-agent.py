import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain

from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class HistoricalContextAgent:
    """
    Agent responsible for analyzing historical context to identify non-core assets
    
    This agent focuses on:
    - Assets from past acquisitions
    - Business units from abandoned strategies
    - Assets from previous market conditions
    """
    
    def __init__(self, llm=None, config=None):
        """
        Initialize the Historical Context Agent
        
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
        # Create prompt template for historical analysis
        self.historical_prompt = PromptTemplate(
            template="""
            You are a corporate historian and strategic analyst specializing in identifying non-core assets. 
            Analyze the following historical data for {company_name}.
            
            Historical information:
            {historical_data}
            
            Acquisition history:
            {acquisition_history}
            
            Identify potential non-core assets based on historical context, focusing on:
            1. Assets from past acquisitions that were never fully integrated
            2. Business units from abandoned strategic directions
            3. Assets that have become less relevant due to market changes
            4. Legacy operations that no longer align with current strategy
            
            For each potential non-core asset identified, provide:
            - Asset name
            - Asset type (acquisition, business unit, market-specific asset, etc.)
            - Year/period of origin or acquisition
            - Original strategic purpose
            - Current strategic alignment (low, medium, high)
            - Reasons for non-core status
            - Potential value if divested
            
            Format your response as a JSON list of historically non-core assets.
            """,
            input_variables=["company_name", "historical_data", "acquisition_history"]
        )
        
        # Create chain using the prompt and the LLM
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=self.historical_prompt,
            output_parser=JsonOutputParser(),
            verbose=self.config.get("verbose", False)
        )
    
    def analyze(self, historical_data: Optional[Dict] = None, 
               acquisition_history: Optional[List[Dict]] = None, 
               company_name: str = "") -> Dict:
        """
        Analyze historical context to identify non-core assets
        
        Args:
            historical_data: Historical company data
            acquisition_history: List of acquisition details
            company_name: Name of the company
            
        Returns:
            Dict: Analysis results
        """
        logger.info(f"Analyzing historical context for {company_name}")
        
        # Initialize results structure
        results = {
            "acquisitions": {},
            "abandoned_strategies": {},
            "market_changes": {}
        }
        
        try:
            # Use LangChain for enhanced analysis if available
            if self.llm and hasattr(self, 'analysis_chain'):
                try:
                    # Prepare input for LLM analysis
                    historical_data_str = json.dumps(historical_data or {}, indent=2)
                    acquisition_history_str = json.dumps(acquisition_history or [], indent=2)
                    
                    # Run analysis chain
                    llm_analysis = self.analysis_chain.run(
                        company_name=company_name,
                        historical_data=historical_data_str,
                        acquisition_history=acquisition_history_str
                    )
                    
                    # Parse result if it's a string
                    if isinstance(llm_analysis, str):
                        try:
                            llm_analysis = json.loads(llm_analysis)
                        except:
                            logger.warning("Failed to parse LLM analysis result as JSON")
                            llm_analysis = {"error": "Failed to parse result"}
                    
                    # Combine with traditional analysis
                    traditional_results = self._traditional_analysis(historical_data, acquisition_history)
                    results = self._merge_results(llm_analysis, traditional_results)
                    
                    logger.info("Enhanced historical context analysis completed with LLM")
                except Exception as e:
                    logger.error(f"Error in LLM-enhanced analysis: {str(e)}")
                    # Fall back to traditional analysis
                    results = self._traditional_analysis(historical_data, acquisition_history)
            else:
                # Perform traditional analysis
                results = self._traditional_analysis(historical_data, acquisition_history)
            
            logger.info("Historical context analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in historical context analysis: {str(e)}")
            raise
    
    def _traditional_analysis(self, historical_data: Optional[Dict] = None, 
                            acquisition_history: Optional[List[Dict]] = None) -> Dict:
        """
        Perform traditional algorithm-based historical analysis
        
        Args:
            historical_data: Historical company data
            acquisition_history: List of acquisition details
            
        Returns:
            Dict: Analysis results
        """
        results = {
            "acquisitions": {},
            "abandoned_strategies": {},
            "market_changes": {}
        }
        
        # Review past acquisitions
        results["acquisitions"] = self._review_past_acquisitions(historical_data, acquisition_history)
        
        # Identify abandoned business units
        results["abandoned_strategies"] = self._identify_abandoned_business_units(historical_data)
        
        # Identify obsolete market assets
        results["market_changes"] = self._identify_obsolete_market_assets(historical_data)
        
        return results
    
    def _review_past_acquisitions(self, historical_data: Optional[Dict] = None, 
                                acquisition_history: Optional[List[Dict]] = None) -> Dict:
        """
        Review past acquisitions and inherited assets
        
        Args:
            historical_data: Historical company data
            acquisition_history: List of acquisition details
            
        Returns:
            Dict: Analysis of acquisition-related assets
        """
        non_integrated_assets = []
        
        # Process acquisition history if available
        if acquisition_history:
            current_year = datetime.now().year
            
            for acquisition in acquisition_history:
                # Extract acquisition details
                acquisition_name = acquisition.get("company", "Unknown Acquisition")
                acquisition_year = acquisition.get("year", 0)
                acquisition_value = acquisition.get("value", 0)
                integration_level = acquisition.get("integration_level", "medium")
                
                # Determine strategic fit based on years elapsed and integration level
                years_since_acquisition = current_year - acquisition_year
                
                # Acquisitions more than 5 years old with low integration are likely non-core
                if years_since_acquisition >= 5 and integration_level.lower() in ["low", "minimal", "none"]:
                    strategic_fit = "poor"
                elif years_since_acquisition >= 3 and integration_level.lower() in ["low", "minimal", "none"]:
                    strategic_fit = "low"
                elif integration_level.lower() in ["low", "minimal", "none"]:
                    strategic_fit = "medium"
                else:
                    strategic_fit = "high"
                
                # Extract assets from the acquisition if available
                acquired_assets = acquisition.get("assets", [])
                
                if acquired_assets:
                    # Process each asset
                    for asset in acquired_assets:
                        asset_name = asset.get("name", "Unknown Asset")
                        asset_value = asset.get("value", 0)
                        asset_integration = asset.get("integration", integration_level)
                        
                        # Only include assets with low integration
                        if asset_integration.lower() in ["low", "minimal", "none"]:
                            non_integrated_assets.append({
                                "acquisition": f"{acquisition_name} ({acquisition_year})",
                                "asset": asset_name,
                                "integration_level": asset_integration,
                                "strategic_fit": strategic_fit,
                                "years_since_acquisition": years_since_acquisition,
                                "original_value": asset_value
                            })
                else:
                    # Include the whole acquisition as a potential non-core asset
                    if strategic_fit in ["poor", "low"]:
                        non_integrated_assets.append({
                            "acquisition": f"{acquisition_name} ({acquisition_year})",
                            "asset": f"{acquisition_name} Operations",
                            "integration_level": integration_level,
                            "strategic_fit": strategic_fit,
                            "years_since_acquisition": years_since_acquisition,
                            "original_value": acquisition_value
                        })
        
        # Also check historical_data for acquisition information if available
        if historical_data and "acquisitions" in historical_data:
            for acq in historical_data["acquisitions"]:
                # Check if this acquisition is already in our list
                acquisition_name = acq.get("name", "Unknown")
                acquisition_year = acq.get("year", 0)
                acquisition_key = f"{acquisition_name} ({acquisition_year})"
                
                # Skip if already processed
                if any(item["acquisition"] == acquisition_key for item in non_integrated_assets):
                    continue
                
                # Process this acquisition
                integration_level = acq.get("integration_status", "medium")
                current_year = datetime.now().year
                years_since_acquisition = current_year - acquisition_year
                
                # Determine strategic fit
                if years_since_acquisition >= 5 and integration_level.lower() in ["low", "minimal", "none"]:
                    strategic_fit = "poor"
                elif years_since_acquisition >= 3 and integration_level.lower() in ["low", "minimal", "none"]:
                    strategic_fit = "low"
                elif integration_level.lower() in ["low", "minimal", "none"]:
                    strategic_fit = "medium"
                else:
                    strategic_fit = "high"
                
                # Include if not well integrated
                if strategic_fit in ["poor", "low"]:
                    non_integrated_assets.append({
                        "acquisition": acquisition_key,
                        "asset": acq.get("primary_asset", f"{acquisition_name} Operations"),
                        "integration_level": integration_level,
                        "strategic_fit": strategic_fit,
                        "years_since_acquisition": years_since_acquisition,
                        "original_value": acq.get("value", 0)
                    })
        
        return {
            "non_integrated_assets": non_integrated_assets
        }
    
    def _identify_abandoned_business_units(self, historical_data: Optional[Dict] = None) -> Dict:
        """
        Identify business units from abandoned expansion strategies
        
        Args:
            historical_data: Historical company data
            
        Returns:
            Dict: Analysis of strategy-related business units
        """
        residual_units = []
        
        if historical_data:
            # Extract strategic initiatives if available
            strategic_initiatives = historical_data.get("strategic_initiatives", [])
            
            for initiative in strategic_initiatives:
                # Check if initiative was abandoned
                status = initiative.get("status", "").lower()
                
                if status in ["abandoned", "discontinued", "scaled back", "deprioritized"]:
                    # Extract details
                    initiative_name = initiative.get("name", "Unknown Initiative")
                    initiative_period = initiative.get("period", "Unknown")
                    
                    # Get associated business units
                    units = initiative.get("business_units", [])
                    
                    if units:
                        for unit in units:
                            unit_name = unit.get("name", "Unknown Unit")
                            unit_status = unit.get("current_status", "unknown").lower()
                            
                            # Only include units that still exist in some form
                            if unit_status not in ["closed", "sold", "divested"]:
                                residual_units.append({
                                    "unit": unit_name,
                                    "strategy": f"{initiative_name} ({initiative_period})",
                                    "current_status": unit_status,
                                    "initiative_status": status,
                                    "headcount": unit.get("headcount", 0),
                                    "annual_cost": unit.get("annual_cost", 0)
                                })
            
            # Also check for direct business units data
            business_units = historical_data.get("business_units", [])
            
            for unit in business_units:
                # Check if unit is from abandoned strategy
                origin = unit.get("origin", "").lower()
                status = unit.get("status", "").lower()
                
                if "strategic shift" in origin or "acquisition" in origin or "diversification" in origin:
                    # Check if current status indicates minimal operations
                    if status in ["minimal operations", "scaled back", "legacy", "maintenance"]:
                        unit_name = unit.get("name", "Unknown Unit")
                        
                        # Skip if already included
                        if any(item["unit"] == unit_name for item in residual_units):
                            continue
                        
                        residual_units.append({
                            "unit": unit_name,
                            "strategy": unit.get("origin_description", origin),
                            "current_status": status,
                            "initiative_status": "abandoned",
                            "headcount": unit.get("headcount", 0),
                            "annual_cost": unit.get("annual_cost", 0)
                        })
        
        return {
            "residual_units": residual_units
        }
    
    def _identify_obsolete_market_assets(self, historical_data: Optional[Dict] = None) -> Dict:
        """
        Identify assets from previous market conditions
        
        Args:
            historical_data: Historical company data
            
        Returns:
            Dict: Analysis of market-related assets
        """
        obsolete_assets = []
        
        if historical_data:
            # Extract market condition information
            market_changes = historical_data.get("market_changes", [])
            if historical_data:
            # Extract market condition information
            market_changes = historical_data.get("market_changes", [])
            
            for change in market_changes:
                # Extract details
                change_type = change.get("type", "Unknown")
                period = change.get("period", "Unknown")
                description = change.get("description", "")
                
                # Look for affected assets
                affected_assets = change.get("affected_assets", [])
                
                for asset in affected_assets:
                    asset_name = asset.get("name", "Unknown Asset")
                    relevance = asset.get("current_relevance", "").lower()
                    
                    # Only include assets with diminishing relevance
                    if relevance in ["declining", "diminishing", "minimal", "low", "none"]:
                        obsolete_assets.append({
                            "asset": asset_name,
                            "market_condition": f"{change_type} ({period})",
                            "current_relevance": relevance,
                            "description": description,
                            "book_value": asset.get("book_value", 0),
                            "estimated_market_value": asset.get("estimated_market_value", 0)
                        })
            
            # Also check for direct assets data
            assets = historical_data.get("assets", [])
            
            for asset in assets:
                # Check if asset relevance is declining
                relevance = asset.get("market_relevance", "").lower()
                reason = asset.get("decline_reason", "")
                
                if relevance in ["declining", "diminishing", "minimal", "low", "none"]:
                    asset_name = asset.get("name", "Unknown Asset")
                    
                    # Skip if already included
                    if any(item["asset"] == asset_name for item in obsolete_assets):
                        continue
                    
                    obsolete_assets.append({
                        "asset": asset_name,
                        "market_condition": asset.get("original_market_condition", "Pre-market shift"),
                        "current_relevance": relevance,
                        "description": reason,
                        "book_value": asset.get("book_value", 0),
                        "estimated_market_value": asset.get("estimated_market_value", 0)
                    })
        
        return {
            "obsolete_assets": obsolete_assets
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
        
        # Process LLM results to enhance traditional analysis if possible
        if isinstance(llm_results, list):
            # Extract asset names from traditional results for matching
            trad_acquisition_assets = set(
                asset["asset"] for asset in traditional_results.get("acquisitions", {}).get("non_integrated_assets", [])
            )
            trad_unit_names = set(
                unit["unit"] for unit in traditional_results.get("abandoned_strategies", {}).get("residual_units", [])
            )
            trad_obsolete_assets = set(
                asset["asset"] for asset in traditional_results.get("market_changes", {}).get("obsolete_assets", [])
            )
            
            # Process each LLM-identified asset
            for llm_asset in llm_results:
                asset_name = llm_asset.get("asset_name", "") or llm_asset.get("name", "")
                asset_type = llm_asset.get("asset_type", "").lower()
                
                # Find which category this asset belongs to
                if asset_type in ["acquisition", "acquired"]:
                    if asset_name in trad_acquisition_assets:
                        # Enhance existing acquisition asset
                        for asset in merged["acquisitions"].get("non_integrated_assets", []):
                            if asset["asset"] == asset_name:
                                asset["llm_strategic_purpose"] = llm_asset.get("original_strategic_purpose", "")
                                asset["llm_reasons"] = llm_asset.get("reasons_for_non_core_status", "")
                                asset["llm_potential_value"] = llm_asset.get("potential_value", "")
                                break
                    else:
                        # Add new acquisition asset
                        if "non_integrated_assets" not in merged["acquisitions"]:
                            merged["acquisitions"]["non_integrated_assets"] = []
                            
                        merged["acquisitions"]["non_integrated_assets"].append({
                            "acquisition": llm_asset.get("year_period", "Unknown"),
                            "asset": asset_name,
                            "integration_level": "low",  # Assumption
                            "strategic_fit": llm_asset.get("current_strategic_alignment", "low"),
                            "llm_strategic_purpose": llm_asset.get("original_strategic_purpose", ""),
                            "llm_reasons": llm_asset.get("reasons_for_non_core_status", ""),
                            "llm_potential_value": llm_asset.get("potential_value", "")
                        })
                
                elif asset_type in ["business unit", "division", "department"]:
                    if asset_name in trad_unit_names:
                        # Enhance existing business unit
                        for unit in merged["abandoned_strategies"].get("residual_units", []):
                            if unit["unit"] == asset_name:
                                unit["llm_strategic_purpose"] = llm_asset.get("original_strategic_purpose", "")
                                unit["llm_reasons"] = llm_asset.get("reasons_for_non_core_status", "")
                                unit["llm_potential_value"] = llm_asset.get("potential_value", "")
                                break
                    else:
                        # Add new business unit
                        if "residual_units" not in merged["abandoned_strategies"]:
                            merged["abandoned_strategies"]["residual_units"] = []
                            
                        merged["abandoned_strategies"]["residual_units"].append({
                            "unit": asset_name,
                            "strategy": llm_asset.get("original_strategic_purpose", "Unknown strategy"),
                            "current_status": "minimal operations",  # Assumption
                            "initiative_status": "abandoned",
                            "llm_strategic_purpose": llm_asset.get("original_strategic_purpose", ""),
                            "llm_reasons": llm_asset.get("reasons_for_non_core_status", ""),
                            "llm_potential_value": llm_asset.get("potential_value", "")
                        })
                
                elif asset_type in ["market-specific", "market", "product"]:
                    if asset_name in trad_obsolete_assets:
                        # Enhance existing obsolete asset
                        for asset in merged["market_changes"].get("obsolete_assets", []):
                            if asset["asset"] == asset_name:
                                asset["llm_strategic_purpose"] = llm_asset.get("original_strategic_purpose", "")
                                asset["llm_reasons"] = llm_asset.get("reasons_for_non_core_status", "")
                                asset["llm_potential_value"] = llm_asset.get("potential_value", "")
                                break
                    else:
                        # Add new obsolete asset
                        if "obsolete_assets" not in merged["market_changes"]:
                            merged["market_changes"]["obsolete_assets"] = []
                            
                        merged["market_changes"]["obsolete_assets"].append({
                            "asset": asset_name,
                            "market_condition": llm_asset.get("year_period", "Unknown market condition"),
                            "current_relevance": "declining",  # Assumption
                            "description": llm_asset.get("original_strategic_purpose", ""),
                            "llm_strategic_purpose": llm_asset.get("original_strategic_purpose", ""),
                            "llm_reasons": llm_asset.get("reasons_for_non_core_status", ""),
                            "llm_potential_value": llm_asset.get("potential_value", "")
                        })
                else:
                    # Default to market changes for any other types
                    if "obsolete_assets" not in merged["market_changes"]:
                        merged["market_changes"]["obsolete_assets"] = []
                        
                    merged["market_changes"]["obsolete_assets"].append({
                        "asset": asset_name,
                        "market_condition": llm_asset.get("year_period", "Unknown market condition"),
                        "current_relevance": "declining",  # Assumption
                        "description": llm_asset.get("original_strategic_purpose", ""),
                        "llm_strategic_purpose": llm_asset.get("original_strategic_purpose", ""),
                        "llm_reasons": llm_asset.get("reasons_for_non_core_status", ""),
                        "llm_potential_value": llm_asset.get("potential_value", "")
                    })
        
        # Add summary of LLM findings
        if isinstance(llm_results, list):
            merged["llm_summary"] = {
                "total_assets_identified": len(llm_results),
                "by_type": self._summarize_llm_results_by_type(llm_results),
                "by_strategic_alignment": self._summarize_llm_results_by_alignment(llm_results)
            }
        
        return merged
    
    def _summarize_llm_results_by_type(self, llm_results: List[Dict]) -> Dict:
        """
        Summarize LLM results by asset type
        
        Args:
            llm_results: List of assets identified by LLM
            
        Returns:
            Dict: Summary by asset type
        """
        type_counts = {}
        
        for asset in llm_results:
            asset_type = asset.get("asset_type", "Unknown")
            
            if asset_type in type_counts:
                type_counts[asset_type] += 1
            else:
                type_counts[asset_type] = 1
        
        return type_counts
    
    def _summarize_llm_results_by_alignment(self, llm_results: List[Dict]) -> Dict:
        """
        Summarize LLM results by strategic alignment
        
        Args:
            llm_results: List of assets identified by LLM
            
        Returns:
            Dict: Summary by strategic alignment
        """
        alignment_counts = {
            "low": 0,
            "medium": 0,
            "high": 0
        }
        
        for asset in llm_results:
            alignment = asset.get("current_strategic_alignment", "").lower()
            
            if alignment in alignment_counts:
                alignment_counts[alignment] += 1
            elif "low" in alignment:
                alignment_counts["low"] += 1
            elif "medium" in alignment or "moderate" in alignment:
                alignment_counts["medium"] += 1
            elif "high" in alignment:
                alignment_counts["high"] += 1
        
        return alignment_counts
