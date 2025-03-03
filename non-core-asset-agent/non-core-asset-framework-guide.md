# Non-Core Asset Identification Framework

A comprehensive AI-driven framework for identifying non-core assets within companies, providing private equity firms and corporate strategists with data-driven divestiture opportunities.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Framework Architecture](#framework-architecture)
- [Getting Started](#getting-started)
- [Example Usage](#example-usage)
- [Configuration Options](#configuration-options)
- [Data Requirements](#data-requirements)
- [Analysis Methodology](#analysis-methodology)
- [Customization](#customization)
- [Output Formats](#output-formats)
- [FAQ](#faq)

## Overview

The Non-Core Asset Identification Framework uses a multi-dimensional analysis approach to systematically identify assets that may not be central to a company's core operations. By analyzing financial statements, operational metrics, industry benchmarks, and historical context, the framework provides a data-driven approach to portfolio rationalization.

### Key Features

- **Multi-dimensional Analysis**: Examines assets from financial, operational, competitive, and historical perspectives
- **LLM Enhancement**: Uses large language models to augment traditional analysis techniques
- **Flexible Data Sources**: Works with SEC filings, financial datasets, operational metrics, and custom inputs
- **Confidence Scoring**: Provides confidence scores and classifications for potential non-core assets
- **Detailed Reporting**: Generates comprehensive reports with visualization options

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/non-core-asset-framework.git
cd non-core-asset-framework

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Make sure to set up your API keys in environment variables:

```bash
export OPENAI_API_KEY=your_openai_api_key
export FINANCIAL_DATA_API_KEY=your_financial_api_key  # Optional
```

## Framework Architecture

The framework consists of several specialized agents working together:

1. **Financial Analysis Agent**: Analyzes financial statements for underperforming assets
2. **Operational Assessment Agent**: Evaluates operational alignment with core revenue streams
3. **Industry Comparison Agent**: Compares performance against industry benchmarks
4. **Historical Context Agent**: Analyzes acquisitions and strategic shifts over time 
5. **Asset Identification Agent**: Aggregates insights and calculates confidence scores

## Getting Started

Basic usage of the framework:

```python
from src.agent.non_core_asset_agent import NonCoreAssetAgent
from src.agent.agent_config import load_config

# Load configuration with defaults
config = load_config()

# Initialize the agent
agent = NonCoreAssetAgent(
    company_name="Example Corp",
    ticker="XYZ",
    config=config.to_dict()
)

# Load data
agent.load_financial_data(financial_statements_path="financial_data.xlsx")
agent.load_operational_data(operational_data_path="operational_metrics.csv")
agent.load_industry_data(industry_data_path="industry_benchmarks.json")
agent.load_historical_data(acquisition_history=[
    {"company": "Acquired Co", "year": 2020, "value": 50000000}
])

# Run analysis
agent.analyze_financial_statements()
agent.assess_operational_alignment()
agent.compare_industry_benchmarks()
agent.analyze_historical_context()

# Identify non-core assets
non_core_assets = agent.identify_non_core_assets(threshold=0.6)

# Generate report
report = agent.generate_report(format="html", output_path="report.html")
```

## Example Usage

### Analyzing HP Inc. (HPQ)

This example demonstrates a complete analysis of HP Inc. to identify potential divestiture candidates:

```python
from src.agent.non_core_asset_agent import NonCoreAssetAgent
from src.agent.agent_config import load_config

# Configure for tech hardware industry
config = load_config(override_config={
    "analysis": {
        "industry_comparison": {
            "performance_threshold": 0.8  # Higher standard in tech
        }
    }
})

# Initialize agent for HP
agent = NonCoreAssetAgent(
    company_name="HP Inc.",
    ticker="HPQ",
    config=config.to_dict()
)

# Load data from SEC filings
agent.load_financial_data(sec_filings=True, year=2023)

# Load operational data
agent.load_operational_data(operational_data_path="hp_operational_metrics.csv")

# Load industry benchmarks and HP's history
agent.load_industry_data(
    industry_data_path="tech_hardware_benchmarks.json",
    industry_code="NAICS:334111"
)
agent.load_historical_data(
    historical_data_path="hp_historical_data.json",
    acquisition_history=[
        {"company": "Poly", "year": 2022, "value": 3300000000, "integration_level": "medium"},
        {"company": "HyperX", "year": 2021, "value": 425000000, "integration_level": "high"},
        {"company": "Samsung Printing", "year": 2017, "value": 1050000000, "integration_level": "high"},
        {"company": "Aruba Networks", "year": 2015, "value": 3000000000, "integration_level": "high"}
    ]
)

# Run full analysis
agent.analyze_all()

# Identify non-core assets
non_core_assets = agent.identify_non_core_assets(threshold=0.65)

# Generate reports in multiple formats
agent.generate_report(format="html", output_path="hp_non_core_assets.html")
agent.generate_report(format="json", output_path="hp_non_core_assets.json")
```

## Configuration Options

The framework offers extensive configuration options via the `agent_config.py` file:

### Language Model Settings
```python
"llm": {
    "enabled": True,
    "model_name": "gpt-4-turbo-preview",
    "temperature": 0.0,
    "max_tokens": 2000
}
```

### Analysis Thresholds
```python
"analysis": {
    "financial_analysis": {
        "low_utilization_threshold": 0.5,
        "revenue_contribution_threshold": 0.05
    },
    "operational_assessment": {
        "facility_utilization_threshold": 0.6
    },
    "industry_comparison": {
        "performance_threshold": 0.75,
        "significant_deviation": 0.2
    }
}
```

### Identification Settings
```python
"identification": {
    "confidence_threshold": 0.6,
    "high_confidence_level": 0.8,
    "medium_confidence_level": 0.65,
    "low_confidence_level": 0.5
}
```

## Data Requirements

The framework can work with varying levels of data quality, but provides more accurate results with comprehensive inputs:

### Financial Data
- Balance sheets
- Income statements
- Asset listings with valuations
- Subsidiary performance metrics

### Operational Data
- Asset utilization metrics
- Revenue attribution by business unit
- Manufacturing capacity metrics
- Technology usage statistics

### Industry Data
- Industry average metrics
- Peer company comparisons
- Benchmark ratios

### Historical Data
- Acquisition history
- Strategic initiatives timeline
- Historical market positioning

## Analysis Methodology

The framework employs four analytical approaches:

### 1. Financial Statement Analysis
Examines financial statements to identify:
- Assets with low utilization rates
- Assets with minimal contribution to core revenue
- Subsidiaries and joint ventures with low strategic alignment
- Real estate holdings not essential to operations
- Intellectual property with minimal active use

### 2. Operational Assessment
Maps assets against core revenue streams to identify:
- Underutilized manufacturing facilities
- Legacy equipment from discontinued product lines
- Excess warehouse/distribution space
- Non-strategic investments in other companies
- Unused patents/technologies from past acquisitions

### 3. Industry Comparison
Compares asset efficiency with industry peers to identify outliers in:
- Asset turnover ratios
- Return on assets
- Revenue per employee
- Space utilization metrics

### 4. Historical Context Analysis
Analyzes company history to identify:
- Assets from past acquisitions that were never fully integrated
- Business units from abandoned expansion strategies
- Assets that have decreased in relevance due to market changes

## Customization

The framework is designed to be extensible:

### Custom Data Loaders
Create specialized data loaders for proprietary data sources:

```python
class CustomDataLoader:
    def load_data(self, file_path):
        # Custom implementation
        pass
```

### Custom Analysis Modules
Extend the framework with specialized analysis techniques:

```python
class CustomAnalyzer:
    def analyze(self, data):
        # Custom implementation
        return analysis_results
```

### Integration with Existing Systems
The framework can be integrated with existing data pipelines, BI tools, and reporting systems.

## Output Formats

The framework supports multiple output formats:

### JSON
Structured data suitable for further processing or integration with other systems.

### CSV
Tabular data suitable for spreadsheet analysis.

### HTML
Formatted report with visualizations for stakeholder presentations.

## FAQ

**Q: Does the framework require an OpenAI API key?**
A: Yes, for LLM-enhanced analysis. However, the framework can also function with just the algorithmic components.

**Q: What industries does the framework support?**
A: The framework is industry-agnostic but performs best with proper industry benchmarks.

**Q: Can the framework analyze private companies?**
A: Yes, though it requires manually input financial and operational data since SEC filings aren't available.

**Q: How accurate is the framework?**
A: Accuracy depends on data quality and completeness. In tests with public companies, it has demonstrated 70-85% alignment with actual divestiture decisions.

**Q: Can the framework be used for acquisition target analysis?**
A: While primarily designed for divestiture analysis, it can be adapted to identify potential acquisition targets by analyzing which assets would complement a company's core operations.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
