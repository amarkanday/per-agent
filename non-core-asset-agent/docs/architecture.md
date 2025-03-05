# Non-Core Asset Identification Framework Architecture

This document describes the architecture of the Non-Core Asset Identification Framework, a modular system designed to identify potential non-core assets within companies through a multi-dimensional analysis approach.

## Architecture Overview

The framework follows a modular, layered architecture with clear separation of concerns:

1. **Orchestration Layer**: Central coordination of the analysis process
2. **Data Layer**: Data acquisition, processing, and storage
3. **Analysis Layer**: Multiple analytical perspectives on company assets
4. **Identification Layer**: Classification of assets as core or non-core
5. **Reporting Layer**: Output generation in various formats
6. **Configuration**: Settings management for all components
7. **LLM Integration**: AI enhancement of analytical capabilities

## Component Breakdown

### Orchestration Layer

- **Non-Core Asset Agent**: The main orchestrator that coordinates all aspects of the analysis process. It initializes other components, manages data flow between them, and provides a unified interface for the user.

### Data Layer

- **Data Loaders**:
  - **SEC Filings Loader**: Extracts financial and operational data from 10-K, 10-Q, and other SEC documents
  - **Web Scraper**: Collects company information from corporate websites and financial portals
  - **Local File Loader**: Reads data from local files (CSV, Excel, JSON, PDF)
  - **Financial API Connector**: Fetches data from financial data providers and market data APIs

- **Data Processors**:
  - **Financial Processor**: Normalizes and structures financial statement data
  - **Operational Processor**: Processes operational metrics
  - **Text Extractor**: Extracts structured data from unstructured text
  - **Document Parser**: Parses different document types into usable formats

- **Data Storage**:
  - **Vector Store**: Uses embeddings to store and retrieve documents semantically
  - **Data Cache**: Caches API responses and processed data for efficiency

### Analysis Layer

- **Financial Analysis Agent**: Examines financial statements to identify:
  - Assets with low utilization rates
  - Subsidiaries with minimal revenue contribution
  - Non-essential real estate holdings
  - Underutilized intellectual property

- **Operational Assessment Agent**: Evaluates operational alignment with core business by identifying:
  - Underutilized manufacturing facilities
  - Legacy equipment
  - Excess warehouse/distribution space
  - Non-strategic investments
  - Unused technologies

- **Industry Comparison Agent**: Benchmarks against industry peers to identify outliers in:
  - Asset turnover ratios
  - Return on assets
  - Revenue per employee
  - Space utilization metrics

- **Historical Context Agent**: Analyzes company history to identify:
  - Assets from past acquisitions that were never fully integrated
  - Business units from abandoned strategies
  - Assets that have decreased in relevance due to market changes

### Identification Layer

- **Asset Scorer**: Assigns preliminary scores to potential non-core assets based on signals from all analyses
- **Confidence Calculator**: Calculates confidence levels based on multiple signals and their weights
- **Asset Classifier**: Applies configurable thresholds to determine which assets are non-core

### Reporting Layer

- **Report Generator**: Creates reports in various formats (JSON, CSV, HTML)
- **Visualizations**: Generates data visualizations for reports, including charts and heatmaps

### Configuration

- **Agent Config**: Manages configuration settings for all components, including:
  - Analysis thresholds
  - API keys and credentials
  - LLM settings
  - Reporting preferences

### LLM Integration

- **LLM Component**: Enhances analysis with language model capabilities by:
  - Extracting additional insights from financial statements
  - Providing justifications for why certain assets are considered non-core
  - Identifying patterns that might not be captured by rule-based analysis
  - Generating recommendations for identified non-core assets

## Data Flow

1. **Input**: The user provides company information and data sources
2. **Data Acquisition**: Data loaders collect information from various sources
3. **Data Processing**: Raw data is transformed into structured formats
4. **Analysis**: The four analytical agents examine the data from different perspectives
5. **Scoring**: Potential non-core assets are scored based on analysis results
6. **Classification**: Assets are classified as core or non-core based on confidence scores
7. **Reporting**: Reports are generated in the user's preferred format

## Integration Points

The framework offers several integration points for customization:

1. **Custom Data Loaders**: Add new data sources by extending the loader classes
2. **Custom Analysis Modules**: Implement new analysis techniques
3. **Custom Confidence Calculators**: Modify how confidence scores are calculated
4. **Custom Report Formats**: Add new output formats for reports
5. **Domain-Specific Knowledge**: Incorporate industry-specific heuristics

## Technology Stack

- **Core Framework**: Python 3.9+
- **Data Processing**: Pandas, NumPy
- **NLP & ML**: LangChain, OpenAI API
- **Vector Database**: FAISS
- **Visualization**: Matplotlib, Seaborn
- **Web Scraping**: BeautifulSoup, Selenium
- **API Clients**: Requests

## Deployment Options

The framework can be deployed in several ways:

1. **Standalone Application**: As a command-line tool or desktop application
2. **Web Service**: As a RESTful API service
3. **Notebook Environment**: Within Jupyter notebooks for interactive analysis
4. **Embedded Component**: As a library integrated into larger financial analysis systems

## Architecture Diagram

```
┌─────────────────┐     ┌──────────────────┐
│                 │     │                  │
│      User       │────▶│  Agent Config    │
│                 │     │                  │
└────────┬────────┘     └──────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐     ┌──────────────────┐
│                 │     │                  │
│  Non-Core Asset │◀───▶│  LLM Component   │
│      Agent      │     │                  │
│                 │     └──────────────────┘
└────────┬────────┘              ▲
         │                       │
         ├───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       │                       ▼
┌─────────────────┐     ┌────────┴────────┐     ┌───────────────┐
│                 │     │                 │     │               │
│   Data Layer    │────▶│  Analysis Layer │────▶│Identification │
│                 │     │                 │     │    Layer      │
└─────────────────┘     └─────────────────┘     └───────┬───────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │                 │
                                               │ Reporting Layer │
                                               │                 │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │                 │
                                               │ Output Formats  │
                                               │ (JSON/CSV/HTML) │
                                               └─────────────────┘
```

## Detailed Data Layer

```
┌───────────────────────────────────────────────────────┐
│                      Data Layer                        │
│                                                        │
│  ┌─────────────────┐         ┌────────────────────┐   │
│  │                 │         │                    │   │
│  │  Data Loaders   │────────▶│  Data Processors   │   │
│  │                 │         │                    │   │
│  └─────────────────┘         └──────────┬─────────┘   │
│     │        │                          │             │
│     ▼        ▼                          ▼             │
│  ┌──────┐ ┌──────┐              ┌─────────────────┐   │
│  │ SEC  │ │ Web  │              │                 │   │
│  │Files │ │Scrape│              │  Vector Store   │   │
│  └──────┘ └──────┘              │                 │   │
│     │        │                  └─────────────────┘   │
│     ▼        ▼                          ▲             │
│  ┌──────┐ ┌──────┐                      │             │
│  │ File │ │ API  │                      │             │
│  │Load  │ │Fetch │                      │             │
│  └──────┘ └──────┘                      │             │
│     │        │                          │             │
│     └────────┼──────────────────────────┘             │
│              │                                         │
└──────────────┼─────────────────────────────────────────┘
               │
               ▼
      To Analysis Layer
```

## Detailed Analysis Layer

```
┌───────────────────────────────────────────────────────┐
│                     Analysis Layer                     │
│                                                        │
│  ┌─────────────────┐         ┌────────────────────┐   │
│  │   Financial     │         │    Operational     │   │
│  │  Analysis Agent │         │ Assessment Agent   │   │
│  └────────┬────────┘         └──────────┬─────────┘   │
│           │                             │             │
│           │         ┌──────────┐        │             │
│           └────────▶│   LLM    │◀───────┘             │
│                     │Component │                      │
│           ┌────────▶│          │◀───────┐             │
│           │         └──────────┘        │             │
│           │                             │             │
│  ┌────────┴────────┐         ┌──────────┴─────────┐   │
│  │    Industry     │         │    Historical      │   │
│  │Comparison Agent │         │  Context Agent     │   │
│  └─────────────────┘         └────────────────────┘   │
│                                                        │
└───────────────────────────────────────────────────────┘
```

## Benefits of This Architecture

1. **Modularity**: Components can be developed, tested, and upgraded independently
2. **Extensibility**: New analysis techniques can be added without disrupting existing functionality
3. **Flexibility**: Works with different data sources and can be configured for various industries
4. **Scalability**: Can handle companies of different sizes and complexity
5. **Hybrid Intelligence**: Combines traditional financial analysis techniques with AI capabilities

This architecture provides a comprehensive framework for identifying non-core assets, helping companies optimize their asset portfolios and focus on core operations.
