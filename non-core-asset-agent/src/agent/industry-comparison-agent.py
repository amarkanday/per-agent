import logging
from typing import Dict, List, Optional, Any, Tuple
import json
import pandas as pd
import numpy as np

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain

from ..utils.logger import setup_logger
from ..utils.metrics import calculate_percentile, calculate_deviation

logger = setup_logger(__name__)

class IndustryComparisonAgent:
    """
    Agent responsible for comparing asset efficiency with industry peers
    
    This agent identifies outliers in:
    - Asset turnover ratios
    - Return on assets
    - Revenue per employee
    - Space utilization metrics
    - Capital expenditure efficiency
    - Inventory turnover
    - Operating margins by segment
    
    It uses both rule-based algorithms and LLM-enhanced analysis to identify
    assets that significantly underperform industry benchmarks.
    """
    
    def __init__(self, llm=None, config=None):
        """
        Initialize the Industry Comparison Agent
        
        Args:
            llm: Language model for enhanced analysis (optional)
            config: Configuration settings
        """
        self.llm = llm
        self.config = config or {}
        self.performance_threshold = self.config.get("performance_threshold", 0.75)
        self.significant_deviation = self.config.get("significant_deviation", 0.2)
        
        # Set up LangChain components if LLM is available
        if self.llm:
            self._setup_chains()
            
    def _setup_chains(self):
        """Set up LangChain chains for analysis"""
        # Create prompt template for industry comparison
        self.comparison_prompt = PromptTemplate(
            template="""
            You are an expert industry analyst specializing in identifying underperforming assets 
            and opportunities for divestiture.
            
            Compare the following company data with industry benchmarks for {company_name}:
            
            COMPANY DATA:
            {company_data}
            
            INDUSTRY BENCHMARKS:
            {industry_data}
            
            Your task is to identify specific assets, business units, or asset categories that 
            significantly underperform industry benchmarks in terms of:
            1. Asset turnover ratios
            2. Return on assets
            3. Revenue per employee
            4. Space utilization metrics
            5. Operating margins
            6. Growth trajectory relative to industry average
            
            For each underperforming asset or category, provide:
            - Asset name or category name
            - Relevant metric(s) where underperformance is observed
            - Company's performance value
            - Industry benchmark value
            - Percentage gap from benchmark
            - Severity rating (Critical, High, Medium, Low)
            - Key factors likely contributing to underperformance
            - Potential value that could be unlocked through divestiture or restructuring
            - Whether the asset appears to be non-core to the company's main operations
            
            Format your response as a JSON list with the following structure:
            [
                {{
                    "asset_name": "Name of the asset or category",
                    "metrics": ["list", "of", "relevant", "metrics"],
                    "company_values": {{"metric_name": value}},
                    "benchmark_values": {{"metric_name": value}},
                    "percentage_gaps": {{"metric_name": value}},
                    "severity": "Critical/High/Medium/Low",
                    "contributing_factors": ["factor1", "factor2"],
                    "potential_value": "Description of value potential",
                    "non_core_assessment": true/false,
                    "justification": "Reasoning for non-core assessment"
                }}
            ]
            
            Focus on substantive underperformance that suggests an asset might be non-core or
            better divested. Prioritize findings with the most significant deviations from benchmarks.
            """,
            input_variables=["company_name", "company_data", "industry_data"]
        )
        
        # Create chain using the prompt and the LLM
        self.comparison_chain = LLMChain(
            llm=self.llm,
            prompt=self.comparison_prompt,
            output_parser=JsonOutputParser(),
            verbose=self.config.get("verbose", False)
        )
        
        # Create prompt for synthesizing findings when multiple metrics suggest an issue
        self.synthesis_prompt = PromptTemplate(
            template="""
            Based on the following metrics comparison between {company_name} and industry benchmarks:
            
            {comparison_results}
            
            Identify the top 3-5 most concerning assets or categories that appear to be 
            significantly underperforming across multiple metrics. For each one, provide:
            
            1. The asset or category name
            2. A synthesis of the performance gaps across all relevant metrics
            3. An overall non-core probability score (0-1)
            4. Whether this asset fits the company's core strategic direction
            5. Estimated financial impact of addressing this underperformance
            
            Format your analysis as a JSON object.
            """,
            input_variables=["company_name", "comparison_results"]
        )
        
        self.synthesis_chain = LLMChain(
            llm=self.llm,
            prompt=self.synthesis_prompt,
            output_parser=JsonOutputParser(),
            verbose=self.config.get("verbose", False)
        )
    
    def compare(self, industry_data: Dict, financial_data: Optional[Dict] = None, 
               operational_data: Optional[Dict] = None, company_name: str = "") -> Dict:
        """
        Compare asset efficiency with industry peers
        
        Args:
            industry_data: Industry benchmark data
            financial_data: Company financial data (optional)
            operational_data: Company operational data (optional)
            company_name: Name of the company
            
        Returns:
            Dict: Comparison results
        """
        logger.info(f"Comparing industry benchmarks for {company_name}")
        
        # Initialize results structure
        results = {
            "summary": {},
            "asset_turnover": {},
            "return_on_assets": {},
            "revenue_per_employee": {},
            "space_utilization": {},
            "operating_margins": {},
            "growth_metrics": {}
        }
        
        try:
            # First, perform traditional algorithmic comparison
            traditional_results = self._traditional_comparison(industry_data, financial_data, operational_data)
            
            # Store initial results
            results.update(traditional_results)
            
            # Calculate summary metrics
            results["summary"] = self._calculate_summary_metrics(traditional_results)
            
            # Enhanced comparison with LLM if available
            if self.llm and hasattr(self, 'comparison_chain'):
                try:
                    # Prepare input for LLM comparison
                    company_data = {}
                    if financial_data:
                        company_data["financial"] = financial_data
                    if operational_data:
                        company_data["operational"] = operational_data
                    
                    company_data_str = json.dumps(company_data, indent=2)
                    industry_data_str = json.dumps(industry_data, indent=2)
                    
                    # Run comparison chain
                    llm_comparison = self.comparison_chain.run(
                        company_name=company_name,
                        company_data=company_data_str,
                        industry_data=industry_data_str
                    )
                    
                    # Parse result if it's a string
                    if isinstance(llm_comparison, str):
                        try:
                            llm_comparison = json.loads(llm_comparison)
                        except:
                            logger.warning("Failed to parse LLM comparison result as JSON")
                            llm_comparison = {"error": "Failed to parse result"}
                    
                    # Synthesize findings if there are multiple metrics
                    if len(traditional_results) > 2 and hasattr(self, 'synthesis_chain'):
                        try:
                            comparison_summary = json.dumps(results, indent=2)
                            synthesis = self.synthesis_chain.run(
                                company_name=company_name,
                                comparison_results=comparison_summary
                            )
                            
                            if isinstance(synthesis, str):
                                try:
                                    synthesis = json.loads(synthesis)
                                except:
                                    logger.warning("Failed to parse synthesis result as JSON")
                            
                            results["llm_synthesis"] = synthesis
                            
                        except Exception as e:
                            logger.error(f"Error in synthesis: {str(e)}")
                    
                    # Add LLM-specific insights
                    results["llm_analysis"] = llm_comparison
                    
                    logger.info("Enhanced industry comparison completed with LLM")
                except Exception as e:
                    logger.error(f"Error in LLM-enhanced comparison: {str(e)}")
                    # We already have traditional results, so we'll continue
            
            logger.info("Industry comparison completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in industry comparison: {str(e)}")
            raise
    
    def _traditional_comparison(self, industry_data: Dict, financial_data: Optional[Dict] = None, 
                              operational_data: Optional[Dict] = None) -> Dict:
        """
        Perform traditional algorithm-based industry comparison
        
        Args:
            industry_data: Industry benchmark data
            financial_data: Company financial data (optional)
            operational_data: Company operational data (optional)
            
        Returns:
            Dict: Comparison results
        """
        results = {}
        
        # Compare asset turnover ratios
        if self._can_calculate_asset_turnover(industry_data, financial_data):
            results["asset_turnover"] = self._compare_asset_turnover(industry_data, financial_data)
        
        # Compare return on assets
        if self._can_calculate_roa(industry_data, financial_data):
            results["return_on_assets"] = self._compare_return_on_assets(industry_data, financial_data)
        
        # Compare revenue per employee
        if self._can_calculate_revenue_per_employee(industry_data, financial_data, operational_data):
            results["revenue_per_employee"] = self._compare_revenue_per_employee(
                industry_data, financial_data, operational_data
            )
        
        # Compare space utilization
        if self._can_calculate_space_utilization(industry_data, operational_data):
            results["space_utilization"] = self._compare_space_utilization(industry_data, operational_data)
        
        # Compare operating margins by segment (if segment data available)
        if self._can_calculate_operating_margins(industry_data, financial_data):
            results["operating_margins"] = self._compare_operating_margins(industry_data, financial_data)
        
        # Compare growth metrics
        if self._can_calculate_growth_metrics(industry_data, financial_data):
            results["growth_metrics"] = self._compare_growth_metrics(industry_data, financial_data)
        
        return results
    
    def _can_calculate_asset_turnover(self, industry_data: Dict, financial_data: Optional[Dict]) -> bool:
        """Check if we have sufficient data to calculate asset turnover comparisons"""
        if not financial_data:
            return False
            
        # Check for revenue and assets in financial data
        has_revenue = "revenue" in financial_data or "sales" in financial_data
        has_assets = "total_assets" in financial_data or "assets" in financial_data
        
        # Check for industry benchmark
        has_industry_benchmark = (
            industry_data and 
            "asset_turnover" in industry_data.get("metrics", {})
        )
        
        return has_revenue and has_assets and has_industry_benchmark
    
    def _can_calculate_roa(self, industry_data: Dict, financial_data: Optional[Dict]) -> bool:
        """Check if we have sufficient data to calculate ROA comparisons"""
        if not financial_data:
            return False
            
        # Check for net income and assets in financial data
        has_net_income = "net_income" in financial_data or "profit" in financial_data
        has_assets = "total_assets" in financial_data or "assets" in financial_data
        
        # Check for industry benchmark
        has_industry_benchmark = (
            industry_data and 
            "return_on_assets" in industry_data.get("metrics", {})
        )
        
        return has_net_income and has_assets and has_industry_benchmark
    
    def _can_calculate_revenue_per_employee(self, industry_data: Dict, 
                                          financial_data: Optional[Dict], 
                                          operational_data: Optional[Dict]) -> bool:
        """Check if we have sufficient data to calculate revenue per employee comparisons"""
        if not financial_data or not operational_data:
            return False
            
        # Check for revenue in financial data
        has_revenue = "revenue" in financial_data or "sales" in financial_data
        
        # Check for employee count in operational data
        has_employees = "employee_count" in operational_data or "employees" in operational_data
        
        # Check for industry benchmark
        has_industry_benchmark = (
            industry_data and 
            "revenue_per_employee" in industry_data.get("metrics", {})
        )
        
        return has_revenue and has_employees and has_industry_benchmark
    
    def _can_calculate_space_utilization(self, industry_data: Dict, operational_data: Optional[Dict]) -> bool:
        """Check if we have sufficient data to calculate space utilization comparisons"""
        if not operational_data:
            return False
            
        # Check for space utilization data
        has_space_data = (
            "facilities" in operational_data or 
            "space_utilization" in operational_data or
            "real_estate" in operational_data
        )
        
        # Check for industry benchmark
        has_industry_benchmark = (
            industry_data and 
            "space_utilization" in industry_data.get("metrics", {})
        )
        
        return has_space_data and has_industry_benchmark
    
    def _can_calculate_operating_margins(self, industry_data: Dict, financial_data: Optional[Dict]) -> bool:
        """Check if we have sufficient data to calculate operating margin comparisons"""
        if not financial_data:
            return False
            
        # Check for segment data with revenues and operating income
        has_segment_data = "segments" in financial_data or "business_units" in financial_data
        
        # Check for industry benchmark
        has_industry_benchmark = (
            industry_data and 
            "operating_margins" in industry_data.get("metrics", {})
        )
        
        return has_segment_data and has_industry_benchmark
    
    def _can_calculate_growth_metrics(self, industry_data: Dict, financial_data: Optional[Dict]) -> bool:
        """Check if we have sufficient data to calculate growth metric comparisons"""
        if not financial_data:
            return False
            
        # Check for historical revenue or income data
        has_historical_data = (
            "historical_revenue" in financial_data or 
            "historical_income" in financial_data or
            "yearly_data" in financial_data
        )
        
        # Check for industry benchmark
        has_industry_benchmark = (
            industry_data and 
            "growth_rates" in industry_data.get("metrics", {})
        )
        
        return has_historical_data and has_industry_benchmark
    
    def _compare_asset_turnover(self, industry_data: Dict, financial_data: Optional[Dict] = None) -> Dict:
        """
        Compare asset turnover ratios with industry peers
        
        Args:
            industry_data: Industry benchmark data
            financial_data: Company financial data
            
        Returns:
            Dict: Asset turnover comparison results
        """
        # Get industry benchmark
        industry_avg = industry_data.get("metrics", {}).get("asset_turnover", 0)
        
        # Calculate company asset turnover
        revenue = financial_data.get("revenue", financial_data.get("sales", 0))
        assets = financial_data.get("total_assets", financial_data.get("assets", 0))
        
        if assets == 0:
            company_value = 0
        else:
            company_value = revenue / assets
        
        # Calculate percentile and deviation
        percentile = calculate_percentile(company_value, industry_avg, industry_data.get("distributions", {}).get("asset_turnover", {}))
        deviation = calculate_deviation(company_value, industry_avg)
        
        # Identify underperforming asset categories
        underperforming_assets = []
        
        # Extract asset categories if available
        asset_categories = self._extract_asset_categories(financial_data)
        
        for category in asset_categories:
            category_turnover = category.get("revenue", 0) / category.get("assets", 1)
            category_benchmark = industry_data.get("by_category", {}).get(category["name"], {}).get("asset_turnover", industry_avg)
            
            if category_turnover < category_benchmark * self.performance_threshold:
                underperforming_assets.append({
                    "category": category["name"],
                    "turnover": category_turnover,
                    "industry_average": category_benchmark,
                    "deviation": (category_turnover - category_benchmark) / category_benchmark,
                    "severity": self._calculate_severity(category_turnover, category_benchmark)
                })
        
        # Sort by severity of deviation
        underperforming_assets.sort(key=lambda x: x["deviation"])
        
        # Return results
        return {
            "company_value": company_value,
            "industry_average": industry_avg,
            "percentile": percentile,
            "deviation": deviation,
            "low_performing_assets": underperforming_assets
        }
    
    def _extract_asset_categories(self, financial_data: Dict) -> List[Dict]:
        """Extract asset categories from financial data"""
        # This implementation would extract asset categories from the financial data
        # with their associated revenue and asset values
        
        # Placeholder for demonstration purposes
        return [
            {"name": "Manufacturing Equipment", "revenue": 25000000, "assets": 30000000},
            {"name": "Storage Facilities", "revenue": 8000000, "assets": 12000000},
            {"name": "Distribution Network", "revenue": 18000000, "assets": 20000000},
            {"name": "Office Properties", "revenue": 5000000, "assets": 15000000}
        ]
    
    def _calculate_severity(self, value: float, benchmark: float) -> str:
        """Calculate severity level based on deviation from benchmark"""
        if benchmark == 0:
            return "Medium"
            
        deviation = (value - benchmark) / benchmark
        
        if deviation <= -0.5:
            return "Critical"
        elif deviation <= -0.3:
            return "High"
        elif deviation <= -0.15:
            return "Medium"
        else:
            return "Low"
    
    def _compare_return_on_assets(self, industry_data: Dict, financial_data: Optional[Dict] = None) -> Dict:
        """
        Compare return on assets with industry peers
        
        Args:
            industry_data: Industry benchmark data
            financial_data: Company financial data
            
        Returns:
            Dict: ROA comparison results
        """
        # Get industry benchmark
        industry_avg = industry_data.get("metrics", {}).get("return_on_assets", 0)
        
        # Calculate company ROA
        net_income = financial_data.get("net_income", financial_data.get("profit", 0))
        assets = financial_data.get("total_assets", financial_data.get("assets", 0))
        
        if assets == 0:
            company_value = 0
        else:
            company_value = net_income / assets
        
        # Calculate percentile and deviation
        percentile = calculate_percentile(company_value, industry_avg, industry_data.get("distributions", {}).get("return_on_assets", {}))
        deviation = calculate_deviation(company_value, industry_avg)
        
        # Identify underperforming asset categories
        underperforming_assets = []
        
        # Extract asset categories if available
        asset_categories = self._extract_asset_categories_with_income(financial_data)
        
        for category in asset_categories:
            category_roa = category.get("income", 0) / category.get("assets", 1)
            category_benchmark = industry_data.get("by_category", {}).get(category["name"], {}).get("return_on_assets", industry_avg)
            
            if category_roa < category_benchmark * self.performance_threshold:
                underperforming_assets.append({
                    "category": category["name"],
                    "roa": category_roa,
                    "industry_average": category_benchmark,
                    "deviation": (category_roa - category_benchmark) / category_benchmark,
                    "severity": self._calculate_severity(category_roa, category_benchmark)
                })
        
        # Sort by severity of deviation
        underperforming_assets.sort(key=lambda x: x["deviation"])
        
        # Return results
        return {
            "company_value": company_value,
            "industry_average": industry_avg,
            "percentile": percentile,
            "deviation": deviation,
            "low_performing_assets": underperforming_assets
        }
    
    def _extract_asset_categories_with_income(self, financial_data: Dict) -> List[Dict]:
        """Extract asset categories with income data from financial data"""
        # This implementation would extract asset categories from the financial data
        # with their associated income and asset values
        
        # Placeholder for demonstration purposes
        return [
            {"name": "Real Estate Holdings", "income": 1200000, "assets": 35000000},
            {"name": "International Subsidiaries", "income": 1500000, "assets": 40000000},
            {"name": "Production Assets", "income": 8000000, "assets": 65000000},
            {"name": "Technology Investments", "income": 1800000, "assets": 25000000}
        ]
    
    def _compare_revenue_per_employee(self, industry_data: Dict, financial_data: Optional[Dict] = None, 
                                    operational_data: Optional[Dict] = None) -> Dict:
        """
        Compare revenue per employee with industry peers
        
        Args:
            industry_data: Industry benchmark data
            financial_data: Company financial data
            operational_data: Company operational data
            
        Returns:
            Dict: Revenue per employee comparison results
        """
        # Get industry benchmark
        industry_avg = industry_data.get("metrics", {}).get("revenue_per_employee", 0)
        
        # Calculate company revenue per employee
        revenue = financial_data.get("revenue", financial_data.get("sales", 0))
        employee_count = operational_data.get("employee_count", operational_data.get("employees", 0))
        
        if employee_count == 0:
            company_value = 0
        else:
            company_value = revenue / employee_count
        
        # Calculate percentile and deviation
        percentile = calculate_percentile(company_value, industry_avg, industry_data.get("distributions", {}).get("revenue_per_employee", {}))
        deviation = calculate_deviation(company_value, industry_avg)
        
        # Identify underperforming business units
        underperforming_units = []
        
        # Extract business units if available
        business_units = self._extract_business_units(financial_data, operational_data)
        
        for unit in business_units:
            unit_rev_per_employee = unit.get("revenue", 0) / unit.get("employees", 1)
            unit_benchmark = industry_data.get("by_function", {}).get(unit["name"], {}).get("revenue_per_employee", industry_avg)
            
            if unit_rev_per_employee < unit_benchmark * self.performance_threshold:
                underperforming_units.append({
                    "unit": unit["name"],
                    "rev_per_employee": unit_rev_per_employee,
                    "industry_average": unit_benchmark,
                    "deviation": (unit_rev_per_employee - unit_benchmark) / unit_benchmark,
                    "severity": self._calculate_severity(unit_rev_per_employee, unit_benchmark)
                })
        
        # Sort by severity of deviation
        underperforming_units.sort(key=lambda x: x["deviation"])
        
        # Return results
        return {
            "company_value": company_value,
            "industry_average": industry_avg,
            "percentile": percentile,
            "deviation": deviation,
            "low_performing_units": underperforming_units
        }
    
    def _extract_business_units(self, financial_data: Dict, operational_data: Dict) -> List[Dict]:
        """Extract business units with revenue and employee data"""
        # This implementation would extract business units from the data
        # with their associated revenue and employee counts
        
        # Placeholder for demonstration purposes
        return [
            {"name": "Administrative Services", "revenue": 3600000, "employees": 20},
            {"name": "Product Development", "revenue": 11000000, "employees": 50},
            {"name": "Sales and Marketing", "revenue": 28000000, "employees": 75},
            {"name": "Manufacturing Operations", "revenue": 42000000, "employees": 120}
        ]
    
    def _compare_space_utilization(self, industry_data: Dict, operational_data: Optional[Dict] = None) -> Dict:
        """
        Compare space utilization metrics with industry peers
        
        Args:
            industry_data: Industry benchmark data
            operational_data: Company operational data
            
        Returns:
            Dict: Space utilization comparison results
        """
        # Get industry benchmark
        industry_avg = industry_data.get("metrics", {}).get("space_utilization", 0)
        
        # Calculate company space utilization
        # This might be an average across facilities
        if "space_utilization" in operational_data:
            company_value = operational_data["space_utilization"]
        else:
            # Extract from facilities data if available
            facilities = operational_data.get("facilities", [])
            if facilities:
                utilization_values = [f.get("utilization", 0) for f in facilities if "utilization" in f]
                company_value = sum(utilization_values) / len(utilization_values) if utilization_values else 0
            else:
                company_value = 0
        
        # Calculate percentile and deviation
        percentile = calculate_percentile(company_value, industry_avg, industry_data.get("distributions", {}).get("space_utilization", {}))
        deviation = calculate_deviation(company_value, industry_avg)
        
        # Identify underperforming spaces
        underperforming_spaces = []
        
        # Extract spaces/locations if available
        spaces = self._extract_spaces(operational_data)
        
        for space in spaces:
            space_utilization = space.get("utilization", 0)
            space_benchmark = industry_data.get("by_location_type", {}).get(space["type"], {}).get("space_utilization", industry_avg)
            
            if space_utilization < space_benchmark * self.performance_threshold:
                underperforming_spaces.append({
                    "location": space["name"],
                    "utilization": space_utilization,
                    "industry_average": space_benchmark,
                    "deviation": (space_utilization - space_benchmark) / space_benchmark,
                    "severity": self._calculate_severity(space_utilization, space_benchmark)
                })
        
        # Sort by severity of deviation
        underperforming_spaces.sort(key=lambda x: x["deviation"])
        
        # Return results
        return {
            "company_value": company_value,
            "industry_average": industry_avg,
            "percentile": percentile,
            "deviation": deviation,
            "low_performing_spaces": underperforming_spaces
        }
    
    def _extract_spaces(self, operational_data: Dict) -> List[Dict]:
        """Extract spaces/locations with utilization data"""
        # This implementation would extract spaces from the operational data
        # with their associated utilization rates
        
        # Placeholder for demonstration purposes
        return [
            {"name": "Corporate Headquarters", "type": "Office", "utilization": 58, "sqft": 120000},
            {"name": "Research Campus", "type": "R&D", "utilization": 52, "sqft": 80000},
            {"name": "Main Production Facility", "type": "Manufacturing", "utilization": 78, "sqft": 250000},
            {"name": "Distribution Center", "type": "Logistics", "utilization": 65, "sqft": 180000}
        ]
    
    def _compare_operating_margins(self, industry_data: Dict, financial_data: Optional[Dict] = None) -> Dict:
        """
        Compare operating margins by segment with industry peers
        
        Args:
            industry_data: Industry benchmark data
            financial_data: Company financial data
            
        Returns:
            Dict: Operating margin comparison results
        """
        # Get industry benchmark
        industry_avg = industry_data.get("metrics", {}).get("operating_margin", 0)
        
        # Calculate company overall operating margin
        if "operating_income" in financial_data and "revenue" in financial_data:
            company_value = financial_data["operating_income"] / financial_data["revenue"]
        else:
            company_value = 0
        
        # Calculate percentile and deviation
        percentile = calculate_percentile(company_value, industry_avg, industry_data.get("distributions", {}).get("operating_margin", {}))
        deviation = calculate_deviation(company_value, industry_avg)
        
        # Identify underperforming segments
        underperforming_segments = []
        
        # Extract segments if available
        segments = self._extract_segments(financial_data)
        
        for segment in segments:
            segment_margin = segment.get("operating_income", 0) / segment.get("revenue", 1)
            segment_benchmark = industry_data.get("by_segment", {}).get(segment["name"], {}).get("operating_margin", industry_avg)
            
            if segment_margin < segment_benchmark * self.performance_threshold:
                underperforming_segments.append({
                    "segment": segment["name"],
                    "margin": segment_margin,
                    "industry_average": segment_benchmark,
                    "deviation": (segment_margin - segment_benchmark) / segment_benchmark,
                    "severity": self._calculate_severity(segment_margin, segment_benchmark)
                })
        
        # Sort by severity of deviation
        underperforming_segments.sort(key=lambda x: x["deviation"])
        
        # Return results
        return {
            "company_value": company_value,
            "industry_average": industry_avg,
            "percentile": percentile,
            "deviation": deviation,
            "low_performing_segments": underperforming_segments
        }
    
    def _extract_segments(self, financial_data: Dict) -> List[Dict]:
        """Extract business segments with revenue and operating income data"""
        # This implementation would extract segments from the financial data
        
        # Placeholder for demonstration purposes
        return [
            {"name": "Consumer Products", "revenue": 45000000, "operating_income": 6500000},
            {"name": "Enterprise Solutions", "revenue": 35000000, "operating_income": 7000000},
            {"name": "Healthcare Services", "revenue": 15000000, "operating_income": 1200000},
            {"name": "International Division", "revenue": 25000000, "operating_income": 2300000}
        ]
    
    def _compare_growth_metrics(self, industry_data: Dict, financial_data: Optional[Dict] = None) -> Dict:
        """
        Compare growth metrics with industry peers
        
        Args:
            industry_data: Industry benchmark data
            financialdef _compare_growth_metrics(self, industry_data: Dict, financial_data: Optional[Dict] = None) -> Dict:
        """
        Compare growth metrics with industry peers
        
        Args:
            industry_data: Industry benchmark data
            financial_data: Company financial data
            
        Returns:
            Dict: Growth metrics comparison results
        """
        # Get industry benchmarks
        industry_revenue_growth = industry_data.get("metrics", {}).get("revenue_growth", 0)
        industry_profit_growth = industry_data.get("metrics", {}).get("profit_growth", 0)
        
        # Calculate company growth rates
        company_revenue_growth = self._calculate_growth_rate(financial_data, "revenue")
        company_profit_growth = self._calculate_growth_rate(financial_data, "net_income")
        
        # Calculate percentiles and deviations
        revenue_percentile = calculate_percentile(
            company_revenue_growth, 
            industry_revenue_growth, 
            industry_data.get("distributions", {}).get("revenue_growth", {})
        )
        profit_percentile = calculate_percentile(
            company_profit_growth, 
            industry_profit_growth, 
            industry_data.get("distributions", {}).get("profit_growth", {})
        )
        
        revenue_deviation = calculate_deviation(company_revenue_growth, industry_revenue_growth)
        profit_deviation = calculate_deviation(company_profit_growth, industry_profit_growth)
        
        # Identify underperforming segments by growth
        underperforming_segments = []
        
        # Extract segments with historical data if available
        segments_with_history = self._extract_segments_with_history(financial_data)
        
        for segment in segments_with_history:
            segment_revenue_growth = self._calculate_segment_growth(segment, "revenue")
            segment_profit_growth = self._calculate_segment_growth(segment, "profit")
            
            segment_revenue_benchmark = industry_data.get("by_segment", {}).get(
                segment["name"], {}).get("revenue_growth", industry_revenue_growth)
            segment_profit_benchmark = industry_data.get("by_segment", {}).get(
                segment["name"], {}).get("profit_growth", industry_profit_growth)
            
            # Check if growth significantly lags industry
            if (segment_revenue_growth < segment_revenue_benchmark * self.performance_threshold or
                segment_profit_growth < segment_profit_benchmark * self.performance_threshold):
                
                underperforming_segments.append({
                    "segment": segment["name"],
                    "revenue_growth": segment_revenue_growth,
                    "profit_growth": segment_profit_growth,
                    "revenue_benchmark": segment_revenue_benchmark,
                    "profit_benchmark": segment_profit_benchmark,
                    "revenue_deviation": (segment_revenue_growth - segment_revenue_benchmark) / max(0.01, segment_revenue_benchmark),
                    "profit_deviation": (segment_profit_growth - segment_profit_benchmark) / max(0.01, segment_profit_benchmark),
                    "severity": self._calculate_growth_severity(segment_revenue_growth, segment_profit_growth,
                                                              segment_revenue_benchmark, segment_profit_benchmark)
                })
        
        # Sort by severity
        underperforming_segments.sort(key=lambda x: x.get("severity_score", 0))
        
        # Return results
        return {
            "revenue_growth": {
                "company_value": company_revenue_growth,
                "industry_average": industry_revenue_growth,
                "percentile": revenue_percentile,
                "deviation": revenue_deviation
            },
            "profit_growth": {
                "company_value": company_profit_growth,
                "industry_average": industry_profit_growth,
                "percentile": profit_percentile,
                "deviation": profit_deviation
            },
            "underperforming_segments": underperforming_segments
        }
    
    def _calculate_growth_rate(self, financial_data: Dict, metric: str) -> float:
        """
        Calculate growth rate for a specific financial metric
        
        Args:
            financial_data: Financial data dictionary
            metric: Metric to calculate growth for (revenue, net_income, etc.)
            
        Returns:
            float: Calculated growth rate
        """
        # Check for historical data in various possible formats
        if f"historical_{metric}" in financial_data:
            historical_data = financial_data[f"historical_{metric}"]
            if isinstance(historical_data, list) and len(historical_data) >= 2:
                current = historical_data[0]
                previous = historical_data[1]
                if previous != 0:
                    return (current - previous) / previous
        
        elif "yearly_data" in financial_data and len(financial_data["yearly_data"]) >= 2:
            years = sorted(financial_data["yearly_data"].keys(), reverse=True)
            if len(years) >= 2:
                current_year = years[0]
                previous_year = years[1]
                
                current = financial_data["yearly_data"][current_year].get(metric, 0)
                previous = financial_data["yearly_data"][previous_year].get(metric, 0)
                
                if previous != 0:
                    return (current - previous) / previous
        
        # Default if no historical data found
        return 0
    
    def _extract_segments_with_history(self, financial_data: Dict) -> List[Dict]:
        """Extract business segments with historical data"""
        # This implementation would extract segments with their historical performance
        
        # Placeholder for demonstration purposes
        return [
            {
                "name": "Consumer Products",
                "history": {
                    "2024": {"revenue": 45000000, "profit": 6500000},
                    "2023": {"revenue": 42000000, "profit": 6000000},
                    "2022": {"revenue": 38000000, "profit": 5500000}
                }
            },
            {
                "name": "Enterprise Solutions",
                "history": {
                    "2024": {"revenue": 35000000, "profit": 7000000},
                    "2023": {"revenue": 31000000, "profit": 6000000},
                    "2022": {"revenue": 28000000, "profit": 5200000}
                }
            },
            {
                "name": "Healthcare Services",
                "history": {
                    "2024": {"revenue": 15000000, "profit": 1200000},
                    "2023": {"revenue": 16000000, "profit": 1500000},
                    "2022": {"revenue": 17000000, "profit": 1800000}
                }
            },
            {
                "name": "International Division",
                "history": {
                    "2024": {"revenue": 25000000, "profit": 2300000},
                    "2023": {"revenue": 22000000, "profit": 2100000},
                    "2022": {"revenue": 21000000, "profit": 2000000}
                }
            }
        ]
    
    def _calculate_segment_growth(self, segment: Dict, metric: str) -> float:
        """
        Calculate growth rate for a specific segment and metric
        
        Args:
            segment: Segment data dictionary with history
            metric: Metric to calculate growth for (revenue, profit, etc.)
            
        Returns:
            float: Calculated growth rate
        """
        if "history" not in segment:
            return 0
            
        history = segment["history"]
        years = sorted(history.keys(), reverse=True)
        
        if len(years) < 2:
            return 0
            
        current_year = years[0]
        previous_year = years[1]
        
        current = history[current_year].get(metric, 0)
        previous = history[previous_year].get(metric, 0)
        
        if previous == 0:
            return 0
            
        return (current - previous) / previous
    
    def _calculate_growth_severity(self, revenue_growth: float, profit_growth: float,
                                 revenue_benchmark: float, profit_benchmark: float) -> Dict:
        """
        Calculate severity rating for growth underperformance
        
        Args:
            revenue_growth: Segment revenue growth
            profit_growth: Segment profit growth
            revenue_benchmark: Industry revenue growth benchmark
            profit_benchmark: Industry profit growth benchmark
            
        Returns:
            Dict: Severity rating with score
        """
        # Calculate deviations
        if revenue_benchmark != 0:
            revenue_deviation = (revenue_growth - revenue_benchmark) / revenue_benchmark
        else:
            revenue_deviation = 0
            
        if profit_benchmark != 0:
            profit_deviation = (profit_growth - profit_benchmark) / profit_benchmark
        else:
            profit_deviation = 0
        
        # Use weighted average of deviations, with profit growth weighted more heavily
        weighted_deviation = 0.4 * revenue_deviation + 0.6 * profit_deviation
        
        # Calculate severity score (0-100, higher is worse)
        severity_score = max(0, min(100, 50 - weighted_deviation * 100))
        
        # Determine severity level
        if severity_score >= 75:
            severity = "Critical"
        elif severity_score >= 50:
            severity = "High"
        elif severity_score >= 25:
            severity = "Medium"
        else:
            severity = "Low"
        
        return {
            "severity": severity,
            "severity_score": severity_score,
            "weighted_deviation": weighted_deviation
        }
    
    def _calculate_summary_metrics(self, results: Dict) -> Dict:
        """
        Calculate summary metrics across all comparison dimensions
        
        Args:
            results: Comparison results from all metrics
            
        Returns:
            Dict: Summary metrics
        """
        # Collect all underperforming assets/segments/units
        all_underperforming = []
        
        # Asset turnover
        if "asset_turnover" in results and "low_performing_assets" in results["asset_turnover"]:
            for asset in results["asset_turnover"]["low_performing_assets"]:
                all_underperforming.append({
                    "name": asset.get("category", "Unknown asset"),
                    "type": "Asset",
                    "metric": "Asset Turnover",
                    "value": asset.get("turnover", 0),
                    "benchmark": asset.get("industry_average", 0),
                    "deviation": asset.get("deviation", 0),
                    "severity": asset.get("severity", "Medium")
                })
        
        # Return on assets
        if "return_on_assets" in results and "low_performing_assets" in results["return_on_assets"]:
            for asset in results["return_on_assets"]["low_performing_assets"]:
                all_underperforming.append({
                    "name": asset.get("category", "Unknown asset"),
                    "type": "Asset",
                    "metric": "Return on Assets",
                    "value": asset.get("roa", 0),
                    "benchmark": asset.get("industry_average", 0),
                    "deviation": asset.get("deviation", 0),
                    "severity": asset.get("severity", "Medium")
                })
        
        # Revenue per employee
        if "revenue_per_employee" in results and "low_performing_units" in results["revenue_per_employee"]:
            for unit in results["revenue_per_employee"]["low_performing_units"]:
                all_underperforming.append({
                    "name": unit.get("unit", "Unknown unit"),
                    "type": "Business Unit",
                    "metric": "Revenue per Employee",
                    "value": unit.get("rev_per_employee", 0),
                    "benchmark": unit.get("industry_average", 0),
                    "deviation": unit.get("deviation", 0),
                    "severity": unit.get("severity", "Medium")
                })
        
        # Space utilization
        if "space_utilization" in results and "low_performing_spaces" in results["space_utilization"]:
            for space in results["space_utilization"]["low_performing_spaces"]:
                all_underperforming.append({
                    "name": space.get("location", "Unknown location"),
                    "type": "Real Estate",
                    "metric": "Space Utilization",
                    "value": space.get("utilization", 0),
                    "benchmark": space.get("industry_average", 0),
                    "deviation": space.get("deviation", 0),
                    "severity": space.get("severity", "Medium")
                })
        
        # Operating margins
        if "operating_margins" in results and "low_performing_segments" in results["operating_margins"]:
            for segment in results["operating_margins"]["low_performing_segments"]:
                all_underperforming.append({
                    "name": segment.get("segment", "Unknown segment"),
                    "type": "Business Segment",
                    "metric": "Operating Margin",
                    "value": segment.get("margin", 0),
                    "benchmark": segment.get("industry_average", 0),
                    "deviation": segment.get("deviation", 0),
                    "severity": segment.get("severity", "Medium")
                })
        
        # Growth metrics
        if "growth_metrics" in results and "underperforming_segments" in results["growth_metrics"]:
            for segment in results["growth_metrics"]["underperforming_segments"]:
                all_underperforming.append({
                    "name": segment.get("segment", "Unknown segment"),
                    "type": "Business Segment",
                    "metric": "Growth Rate",
                    "value": segment.get("revenue_growth", 0),
                    "benchmark": segment.get("revenue_benchmark", 0),
                    "deviation": segment.get("revenue_deviation", 0),
                    "severity": segment.get("severity", {}).get("severity", "Medium")
                })
        
        # Count items by severity
        severity_counts = {
            "Critical": len([item for item in all_underperforming if item["severity"] == "Critical"]),
            "High": len([item for item in all_underperforming if item["severity"] == "High"]),
            "Medium": len([item for item in all_underperforming if item["severity"] == "Medium"]),
            "Low": len([item for item in all_underperforming if item["severity"] == "Low"])
        }
        
        # Calculate overall company performance
        overall_metrics = {}
        
        # Get company-wide values for each metric
        if "asset_turnover" in results:
            overall_metrics["asset_turnover"] = {
                "value": results["asset_turnover"].get("company_value", 0),
                "benchmark": results["asset_turnover"].get("industry_average", 0),
                "percentile": results["asset_turnover"].get("percentile", 0),
                "deviation": results["asset_turnover"].get("deviation", 0)
            }
        
        if "return_on_assets" in results:
            overall_metrics["return_on_assets"] = {
                "value": results["return_on_assets"].get("company_value", 0),
                "benchmark": results["return_on_assets"].get("industry_average", 0),
                "percentile": results["return_on_assets"].get("percentile", 0),
                "deviation": results["return_on_assets"].get("deviation", 0)
            }
        
        # Identify potential non-core assets
        potential_non_core = []
        
        # Critical and high severity items are potential non-core assets
        for item in all_underperforming:
            if item["severity"] in ["Critical", "High"]:
                # Check if this item already exists in the list
                existing = next((x for x in potential_non_core if x["name"] == item["name"]), None)
                
                if existing:
                    # Add this metric to the existing item
                    existing["metrics"].append(item["metric"])
                    existing["count"] += 1
                else:
                    # Add new item
                    potential_non_core.append({
                        "name": item["name"],
                        "type": item["type"],
                        "metrics": [item["metric"]],
                        "count": 1,
                        "severity": item["severity"]
                    })
        
        # Sort by number of underperforming metrics
        potential_non_core.sort(key=lambda x: (x["count"], x["severity"] == "Critical"), reverse=True)
        
        # Return summary
        return {
            "total_underperforming": len(all_underperforming),
            "by_severity": severity_counts,
            "overall_metrics": overall_metrics,
            "potential_non_core_assets": potential_non_core[:5],  # Top 5 most consistently underperforming
            "all_underperforming": all_underperforming
        }
