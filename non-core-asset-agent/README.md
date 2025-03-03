# Non-Core Asset Identification Agent

An AI agent framework for identifying non-core assets within companies.

## Overview

This framework provides a systematic approach to identify potential non-core assets within companies through:

1. Financial Statement Analysis
2. Operational Assessment
3. Industry Comparison
4. Historical Context Analysis

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from src.agent.non_core_asset_agent import NonCoreAssetAgent

# Initialize agent
agent = NonCoreAssetAgent(company_name="Acme Industries", ticker="ACME")

# Load data
agent.load_financial_data(financial_statements_path="financial_data.xlsx")

# Run analyses
agent.analyze_financial_statements()
agent.assess_operational_alignment()
agent.compare_industry_benchmarks()
agent.analyze_historical_context()

# Identify non-core assets
non_core_assets = agent.identify_non_core_assets(threshold=0.7)

# Generate report
report = agent.generate_report(format="html", output_path="report.html")
```
