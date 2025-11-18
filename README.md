# Survey Insight Pipeline

An AI-powered customer survey analysis system that transforms raw insurance customer feedback into actionable business insights using AutoGen multi-agent framework and Model Context Protocol (MCP).

## Overview

This project implements a 4-step, end-to-end pipeline that converts unstructured customer survey CSV data into:
- Enriched, analytics-ready CSV files
- Executive-ready visualizations
- Decision-ready insights for senior leadership


## Architecture

```
┌───────────────────────────────────────-─────────────────┐
│                   Streamlit UI / CLI                    │
│            (User Interface Layer)                       │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│          SurveyInsightAgent (MCP Client)                │
│            AutoGen RoundRobin Team                      │
│         - Orchestrates 4-step workflow                  │
│         - Calls MCP tools sequentially                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│                    MCP Server                          │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tool 1: TopicExtraction                        │   │
│  │  - LLM topic extraction (GPT-4o-mini)           │   │
│  │  - Sentiment analysis                           │   │
│  └─────────────────────────────────────────────────┘   │
│                       │                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tool 2: TopicClustering                        │   │
│  │  - OpenAI embeddings generation                 │   │
│  │  - KMeans clustering (12 clusters)              │   │
│  └─────────────────────────────────────────────────┘   │
│                       │                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tool 3: ClusterLabelling                       │   │
│  │  - LLM theme naming (GPT-4o-mini)               │   │
│  │  - Data explosion (1 row per topic)             │   │
│  └─────────────────────────────────────────────────┘   │
│                       │                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tool 4: businessInsight                        │   │
│  │  - Aggregations & analytics                     │   │
│  │  - Matplotlib visualizations (4 plots)          │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                           │
│  input.csv → topics.csv → clusters.csv → output.csv     │
│                    + 4 PNG visualizations               │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Agent Framework**: AutoGen 
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small
- **Clustering**: scikit-learn (KMeans)
- **Data Processing**: pandas, numpy
- **Visualization**: matplotlib
- **UI**: Streamlit
- **MCP**: FastMCP
- **Environment**: Python 3.10+

## Setup Instructions


### Step 1: Clone the Repository

```bash
git clone https://github.com/ebythomas23/Customer-Survey-Insight.git
cd Customer-Survey-Insight
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```


### Step 4: Configure Environment Variables

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and replace `your_openai_api_key_here` with your actual OpenAI API key:

### Step 5: Upload Data 

**If using command line interface:**

Inside the `data/` directory and place your input CSV file as input.csv

**If using Streamlit UI:** Skip this step - you'll upload the CSV through the web interface.


### Step 6: Usage

#### Option 1: Streamlit Web Interface (Recommended)

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open browser** (usually auto-opens at `http://localhost:8501`)

4. **Upload CSV** and click "Run Analysis Pipeline"

5. **View results**: The app displays:
   - Pipeline progress in real-time
   - Generated visualizations
   - Preview of enriched output data
   - Download button for final CSV

#### Option 2: Command Line Interface

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Ensure input data** is at `data/input.csv`

3. **Run the pipeline:**
   ```bash
   python main.py
   ```

4. **Check outputs** in the `data/` directory:
   - `data/output.csv` - Enriched, analytics-ready data
   - `data/plot_*.png` - Visualization files

## The 4-Step Pipeline

### Step 1: Topic Extraction
- **Tool**: `TopicExtraction`
- **Input**: `data/input.csv`
- **Output**: `data/df_with_topics.csv`
- **Process**: 
  - Extracts 2-5 key topics from each survey response using GPT-4o-mini
  - Adds metadata: topics list, supporting quote, reasoning, sentiment

### Step 2: Topic Clustering
- **Tool**: `TopicClustering`
- **Input**: `data/df_with_topics.csv`
- **Output**: `data/df_with_clusters.csv`
- **Process**:
  - Generates embeddings for unique topics
  - Groups similar topics using KMeans (default: 12 clusters)
  - Assigns cluster IDs to each topic

### Step 3: Cluster Labelling
- **Tool**: `ClusterLabelling`
- **Input**: `data/df_with_clusters.csv`
- **Output**: `data/output.csv`
- **Process**:
  - Uses LLM to assign business-friendly labels to clusters
  - Examples: "Claims process complexity", "Claims turnaround delays"
  - Explodes data to one row per topic with its theme label

### Step 4: Business Insights & Visualization
- **Tool**: `businessInsight`
- **Input**: `data/output.csv`
- **Outputs**:
  - `data/plot_top_pain_points.png` - Top N pain points bar chart
  - `data/heatmap_pain_points_by_product.png` - Pain points by product heatmap
  - `data/theme_severity_stacked.png` - Theme severity by sentiment (100% stacked)
  - `data/theme_trends_over_time.png` - Monthly theme trends line chart
  - Executive summary with key insights


## Configuration

### Model Configuration

Edit `config/constants.py` to change the OpenAI model:

```python
MODEL_OPENAI = 'gpt-4o-mini'  # or 'gpt-4o', 'gpt-4-turbo', etc.
```

### Clustering Parameters

Modify clustering in `tools/topic_clustering.py`:

```python
num_clusters: int = 12  # Adjust number of theme clusters
```

### Visualization Settings

Adjust top N themes in `tools/business_insight.py`:

```python
top_n: int = 5  # Number of top themes to highlight
```

## Project Structure

```
.
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables 
├── main.py                       # CLI entry point
├── streamlit_app.py              # Web UI entry point
│
├── agents/
│   └── SurveyInsightAgent.py     # Main orchestrator agent
│
├── config/
│   └── constants.py              # Configuration constants
│
├── data/                         # Data directory 
│   ├── input.csv                 # Input survey data
│   ├── df_with_topics.csv        # After Step 1
│   ├── df_with_clusters.csv      # After Step 2
│   ├── output.csv                # Final enriched output
│   └── *.png                     # Generated visualizations
│
├── MCP/
│   ├── server.py                 # MCP server implementation
│   └── mcp_tools.py              # MCP client tools configuration
│
├── models/
│   └── openai_model_client.py    # OpenAI client wrapper
│
├── prompts/
│   └── system_prompt.py          # Agent system prompts
│
├── teams/
│   └── survey_insight.py         # Team configuration
│
└── tools/
    ├── topics_extraction.py      # Step 1: Topic extraction
    ├── topic_clustering.py       # Step 2: Clustering
    ├── cluster_labelling.py      # Step 3: Labelling
    └── business_insight.py       # Step 4: Insights & plots
```

## Business Insights

The pipeline transforms raw survey data into two deliverables: a structured CSV file (`output.csv`) ready for Power BI/Tableau dashboards, and four analytical charts that answer critical business questions. Together, these outputs enable executives to identify top customer pain points, understand product-specific issues, assess problem severity through sentiment analysis, and track improvement trends over time.

### The Four Charts

All charts are saved as PNG files in the `data/` folder.

<table>
<tr>
<td width="50%">

#### 1. Top Customer Pain Points
[`plot_top_pain_points.png`](data/plot_top_pain_points.png)

![Top Pain Points](data/plot_top_pain_points.png)

This bar chart shows which issues customers mention most often. If "Claims Processing" appears 150 times and "Website Issues" appears 30 times, you know where to focus first.

</td>
<td width="50%">

#### 2. Pain Points by Product
[`heatmap_pain_points_by_product.png`](data/heatmap_pain_points_by_product.png)

![Pain Points by Product](data/heatmap_pain_points_by_product.png)

This heatmap shows which problems affect which products. For example, if "Combined Insurance" has many complaints about billing but "Travel Insurance" doesn't, you know the issue is product-specific.

</td>
</tr>
<tr>
<td width="50%">

#### 3. Theme Severity by Sentiment
[`theme_severity_stacked.png`](data/theme_severity_stacked.png)

![Theme Severity](data/theme_severity_stacked.png)

This shows how angry or satisfied customers are about each issue. A theme that's 80% negative is more urgent than one that's 50% neutral, even if mentioned the same number of times.

</td>
<td width="50%">

#### 4. Theme Trends Over Time
[`theme_trends_over_time.png`](data/theme_trends_over_time.png)

![Theme Trends](data/theme_trends_over_time.png)

This line chart tracks complaints month by month. If complaints about "Call Wait Times" are going down, your improvements are working. If they're going up, you need to act quickly.

</td>
</tr>
</table>

### Adding More Charts or features 

To add new visualizations, simply add new plot functions to `tools/business_insight.py` or register new tool and addin `MCP/server.py`. The system automatically makes them available to the agent.


## Improvement Plan for the Project


### 1. Monitoring, Tracing, and Cost Tracking
- Integrate AgentOps for monitoring, tracing, and observability across all agent steps.
- Record execution flow for each tool invocation in the pipeline.
- Track and compare cost and token usage across different models, including lighter ones like **gpt-5-mini**.

### 2. Explore Multi-Agent Architectures
- Try out different multi-agent patterns such as **SelectorGroupChat** and other routing/composer architectures.
- Benchmark each option on output quality, speed, and cost.
- Select the most effective architecture for this workflow.

### 3. Embeddings and Tool Definition Improvements
- Revisit embedding model selection and tuning for topic extraction and clustering.
- Improve chunking strategy and embedding dimensionality choices.
- Clean up and refine all MCP tool definitions for clearer agent interaction.

### 4. Logging for MCP Server
- Add structured logging for every MCP tool call.
- Capture success/failure states, latency, and payload sizes.
- Store logs in a consistent format to support analysis and debugging.

### 5. Fully-Defined MCP Server Setup and Hosting
- Build a clean, modular, and well-documented MCP server.
- Host it locally or remotely for reliable agent access.
- Use AutoGen’s **Workbench** to test tool flows end-to-end and validate behaviour.

### 6. Human-in-the-Loop for Top-N Insights and visualisation 
- Add a review step where users can adjust or confirm the top-N extracted topics.
- Define the exact visualisations needed (bar charts, cluster scatter, word clouds, sentiment breakdown).
- Create an agent that generates the exact graph/plot requested by the user using the processed data.