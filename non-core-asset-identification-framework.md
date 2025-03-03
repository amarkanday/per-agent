# Non-Core Asset Identification Agent Framework

This documentation covers the AI agent framework designed to systematically identify non-core assets within companies.

## Table of Contents
- [Overview](#overview)
- [Core Components](#core-components)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Data Requirements](#data-requirements)
- [Analysis Methodology](#analysis-methodology)
- [Reporting](#reporting)
- [Example Implementation](#example-implementation)

## Overview

The Non-Core Asset Identification Agent is a Python framework that analyzes company data across financial, operational, industry, and historical dimensions to identify potential non-core assets that might be candidates for divestiture, restructuring, or repositioning.

## Core Components

The framework consists of several integrated components:

1. **Data Ingestion Layer** - Flexible mechanisms to import data from various file formats and direct inputs
2. **Multi-dimensional Analysis Engine** - Four analytical modules examining different aspects of asset utilization and alignment
3. **Asset Identification System** - Algorithms to compile, score, and rank potential non-core assets
4. **Reporting Module** - Methods to generate reports in various formats

## Installation

```bash
# Currently available as a Python package
pip install non-core-asset-agent

# Dependencies
# - pandas
# - numpy
# - matplotlib (for certain visualizations)
# - jinja2 (for HTML reports)
```

## Basic Usage

```python
from non_core_asset_agent import NonCoreAssetAgent

# Initialize the agent
agent = NonCoreAssetAgent(company_name="Acme Industries", ticker="ACME")

# Load data
agent.load_financial_data(financial_statements_path="financial_data.xlsx")
agent.load_operational_data(operational_data_path="operations.csv")
agent.load_industry_data(industry_data_path="industry_benchmarks.json")
agent.load_historical_data(acquisition_history=[
    {"year": 2019, "company": "TechSys Solutions", "value": 42000000},
    {"year": 2020, "company": "Global Manufacturing", "value": 85000000}
])

# Run analyses
agent.analyze_financial_statements()
agent.assess_operational_alignment()
agent.compare_industry_benchmarks()
agent.analyze_historical_context()

# Identify non-core assets with a confidence threshold
non_core_assets = agent.identify_non_core_assets(threshold=0.65)

# Generate report
report = agent.generate_report(format="html", output_path="non_core_asset_report.html")
```

## Data Requirements

The agent can work with varying levels of data quality, but its accuracy improves with more comprehensive inputs:

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

The framework employs four distinct analytical approaches:

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

## Reporting

The agent can generate reports in multiple formats:

### JSON Format
Structured data suitable for further processing or integration with other systems.

### CSV Format
Tabular data suitable for spreadsheet analysis.

### HTML Format
Formatted report with visualizations for stakeholder presentations.

## Example Implementation

```python
import os
import json
import pandas as pd
from non_core_asset_agent import NonCoreAssetAgent

# Initialize agent
agent = NonCoreAssetAgent(company_name="Diversified Holdings Inc.", ticker="DHI")

# Load data from multiple sources
agent.load_financial_data(financial_statements_path="financial_data_2023.xlsx")

# Operational data from dictionary
operational_data = {
    "manufacturing": {
        "facilities": [
            {"name": "Plant A", "utilization": 0.87, "revenue_contribution": 0.35},
            {"name": "Plant B", "utilization": 0.35, "revenue_contribution": 0.08},
            {"name": "Plant C", "utilization": 0.92, "revenue_contribution": 0.42}
        ]
    },
    "distribution": {
        "centers": [
            {"name": "Northeast Hub", "utilization": 0.42, "cost": 1850000},
            {"name": "Western Distribution", "utilization": 0.88, "cost": 2100000}
        ]
    }
}
agent.load_operational_data(operational_data=operational_data)

# Run all analyses
agent.analyze_financial_statements()
agent.assess_operational_alignment()
agent.compare_industry_benchmarks()
agent.analyze_historical_context()

# Identify non-core assets with high confidence only
high_confidence_assets = agent.identify_non_core_assets(threshold=0.8)

# Generate comprehensive report
agent.generate_report(format="html", output_path="dhi_non_core_assets.html")
```

The resulting report would highlight assets like Plant B and the Northeast Hub as potential non-core assets based on their low utilization and minimal contribution to core revenue.
