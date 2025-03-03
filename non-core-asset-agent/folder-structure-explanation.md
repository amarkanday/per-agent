# Non-Core Asset Identification Framework Directory Structure

This document explains the organization of the Non-Core Asset Identification Framework codebase and the purpose of each component.

## Directory Overview

```
non-core-asset-agent/
│
├── src/                     # Source code
│   ├── agent/               # Main agent coordination
│   ├── data/                # Data handling components
│   ├── analysis/            # Analytical engines
│   ├── identification/      # Asset identification logic
│   ├── reporting/           # Report generation
│   └── utils/               # Utility functions
│
├── examples/                # Example usage scripts
├── tests/                   # Unit and integration tests
├── data/                    # Data storage
├── docs/                    # Documentation
└── notebooks/               # Jupyter notebooks
```

## Source Code (`src/`)

The `src` directory contains all the framework's source code, organized into logical components.

### Agent Components (`src/agent/`)

These are the primary entry points and coordination components.

- **non_core_asset_agent.py**: Main orchestration class that coordinates all sub-agents
- **agent_config.py**: Configuration management for all components
- **financial_analysis_agent.py**: Agent for financial statement analysis
- **operational_assessment_agent.py**: Agent for operational alignment assessment
- **industry_comparison_agent.py**: Agent for industry benchmark comparison
- **historical_context_agent.py**: Agent for historical context analysis
- **asset_identification_agent.py**: Agent for non-core asset identification

### Data Components (`src/data/`)

Components responsible for data acquisition, processing, and storage.

#### Data Loaders (`src/data/loaders/`)

- **sec_loader.py**: Downloads and parses SEC filings (10-K, 10-Q, etc.)
- **web_loader.py**: Scrapes websites for company information
- **file_loader.py**: Loads data from local files (CSV, Excel, PDF, etc.)
- **api_connector.py**: Connects to financial and industry data APIs

#### Data Processors (`src/data/processors/`)

- **financial_processor.py**: Processes financial statements into structured format
- **operational_processor.py**: Processes operational metrics
- **text_extractor.py**: Extracts structured data from unstructured text
- **document_parser.py**: Parses different document types

#### Data Storage (`src/data/storage/`)

- **vector_store.py**: Vector database for document embeddings
- **data_cache.py**: Caching mechanisms for API responses and processed data

### Analysis Components (`src/analysis/`)

Engines for performing different types of analysis.

- **financial_analysis.py**: Analyzes financial statements for non-core indicators
- **operational_assessment.py**: Evaluates operational alignment with core business
- **industry_comparison.py**: Compares metrics against industry benchmarks
- **historical_context.py**: Analyzes acquisitions and strategic shifts

### Identification Components (`src/identification/`)

Logic for identifying and classifying non-core assets.

- **asset_scorer.py**: Assigns preliminary scores to potential non-core assets
- **confidence_calculator.py**: Calculates confidence levels based on multiple signals
- **asset_classifier.py**: Applies thresholds to determine core vs non-core classification

### Reporting Components (`src/reporting/`)

Output generation for analysis results.

- **report_generator.py**: Creates reports in various formats (JSON, CSV, HTML)
- **visualizations.py**: Generates data visualizations for reports
- **templates/**: HTML templates for formatted reports

### Utility Functions (`src/utils/`)

Common utilities used across the framework.

- **logger.py**: Logging configuration and functions
- **validators.py**: Data validation helpers
- **metrics.py**: Common calculation functions for financial metrics

## Examples (`examples/`)

Sample scripts demonstrating framework usage.

- **basic_usage.py**: Simple example showing basic framework functionality
- **advanced_usage.py**: More complex example with custom configurations
- **sec_filing_analysis.py**: Example focusing on SEC filing analysis
- **industry_comparison_example.py**: Example focusing on peer comparison
- **analyze_hp_example.py**: Complete example analyzing HP Inc. (HPQ)

## Tests (`tests/`)

Unit and integration tests for ensuring code quality.

- **test_agent.py**: Tests for main agent functionality
- **test_data_loaders.py**: Tests for data loading components
- **test_analysis.py**: Tests for analysis modules
- **test_identification.py**: Tests for identification logic

## Data (`data/`)

Directory for storing data files.

- **sample/**: Sample data files for testing and examples
  - **financial_statements.xlsx**: Sample financial data
  - **operational_metrics.csv**: Sample operational metrics
  - **industry_benchmarks.json**: Sample industry benchmarks
- **cache/**: Directory for cached API responses and intermediate results

## Documentation (`docs/`)

Comprehensive documentation for the framework.

- **api_reference.md**: API documentation for all classes and functions
- **getting_started.md**: Quick start guide
- **data_requirements.md**: Detailed explanation of data format requirements
- **configuration.md**: Configuration options reference
- **examples.md**: Additional examples and use cases

## Jupyter Notebooks (`notebooks/`)

Interactive notebooks for exploration and visualization.

- **exploration.ipynb**: Data exploration techniques
- **visualization.ipynb**: Result visualization examples
- **case_studies/**: Detailed case studies of different companies
  - **manufacturing_example.ipynb**: Analysis of a manufacturing company
  - **technology_example.ipynb**: Analysis of a technology company

## Usage Flow

The typical usage flow of the framework follows these steps:

1. **Configuration**: Set up the framework with appropriate settings (via `agent_config.py`)
2. **Initialization**: Create an instance of `NonCoreAssetAgent` with company information
3. **Data Loading**: Load data using the various loader methods
4. **Analysis**: Run the analytical modules (financial, operational, industry, historical)
5. **Identification**: Identify and classify non-core assets based on analysis results
6. **Reporting**: Generate reports in the desired format

## Extension Points

The framework is designed to be extended through:

1. **Custom Data Loaders**: Add new data sources by extending the loader classes
2. **Custom Analysis Modules**: Implement new analysis techniques
3. **Custom Confidence Calculators**: Modify how confidence scores are calculated
4. **Custom Report Formats**: Add new output formats for reports
5. **Domain-Specific Knowledge**: Incorporate industry-specific heuristics

## Integration with LangChain

The framework integrates with LangChain in several key areas:

1. **Document Processing**: Using LangChain's document loaders and processing capabilities
2. **Enhanced Analysis**: Using LLMs to augment traditional financial and operational analysis
3. **Vector Storage**: Storing and retrieving documents with semantic search
4. **Chain Composition**: Building analytical pipelines through LangChain's chain mechanisms
5. **Agent Orchestration**: Using LangChain's agent framework for coordinating specialized agents

This integration allows the framework to combine traditional financial analysis techniques with the power of large language models, providing deeper insights into non-core asset identification.
