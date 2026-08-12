# AI Business Analyst Platform

An end-to-end AI-powered Business Analytics Platform that enables organizations to upload datasets, analyze business performance, detect anomalies, forecast future trends, and interact with data using natural language through a Retrieval-Augmented Generation (RAG) system powered by Gemini.

---

# Project Overview

The AI Business Analyst Platform combines Data Analytics, Machine Learning, and Generative AI to automate business intelligence workflows.

Users can:

- Upload business datasets
- Generate Data Quality Reports
- Perform Exploratory Data Analysis (EDA)
- Generate Automated Business Insights
- Detect Anomalies
- Forecast Future Trends
- Interact with data using AI Chat
- Generate Executive Reports

---

# Features

## Data Quality Analysis

- Missing value analysis
- Duplicate record detection
- Data type validation
- Dataset summary statistics

## Exploratory Data Analysis (EDA)

- Numerical feature analysis
- Distribution analysis
- Correlation analysis
- Statistical summaries

## Business Insights Engine

- Revenue analysis
- Profitability analysis
- Regional performance analysis
- Product category analysis
- Executive recommendations

## Interactive Dashboard

- Total Sales KPI
- Total Profit KPI
- Profit Margin KPI
- Sales by Region
- Category Performance
- Interactive Visualizations

## Anomaly Detection

### Z-Score Method

Detects statistical outliers using standard deviation thresholds.

### Isolation Forest

Detects multivariate anomalies using machine learning.

Features:

- Outlier Detection
- Root Cause Identification
- Anomaly Scoring
- Business Risk Monitoring

## Predictive Forecasting

- Monthly Forecasting
- Weekly Forecasting
- Daily Forecasting
- Confidence Intervals
- Trend Analysis
- Future Projections

## AI Business Analyst Chat

Powered by:

- Google Gemini
- Sentence Transformers
- FAISS Vector Database
- Retrieval-Augmented Generation (RAG)

Users can ask questions such as:

- Which region performs best?
- What products generate highest profit?
- Which category has highest sales?
- Give me business recommendations.
- Summarize this dataset.

---

# Architecture

```text
CSV Dataset
      │
      ▼
Data Loader
      │
      ▼
Data Cleaning
      │
      ▼
Data Profiling
      │
      ▼
EDA Analysis
      │
      ▼
Business Insights
      │
      ├──────────────► Dashboard
      │
      ├──────────────► Anomaly Detection
      │
      ├──────────────► Forecasting
      │
      ▼
Context Builder
      │
      ▼
Document Processing
      │
      ▼
Sentence Embeddings
      │
      ▼
FAISS Vector Store
      │
      ▼
Retriever
      │
      ▼
Gemini LLM
      │
      ▼
AI Business Analyst Chat
```

---

# Technology Stack

## Frontend

- Streamlit

## Data Processing

- Pandas
- NumPy

## Visualization

- Plotly
- Matplotlib

## Machine Learning

- Scikit-Learn
- Isolation Forest
- Ridge Regression

## AI & RAG

- Google Gemini
- Sentence Transformers
- FAISS
- Retrieval-Augmented Generation (RAG)

## Environment Management

- Python Dotenv

---

# Project Structure

```text
ai-business-analyst/

├── app/
│   ├── main.py
│   ├── pages/
│   └── utils/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── embeddings/
│
├── reports/
│
├── screenshots/
│
├── src/
│   ├── anomaly_detection/
│   ├── eda/
│   ├── forecasting/
│   ├── ingestion/
│   ├── insights/
│   ├── kpi/
│   ├── preprocessing/
│   ├── profiling/
│   └── rag/
│
├── tests/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/your-username/ai-business-analyst.git

cd ai-business-analyst
```

## Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Gemini API

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

# Run Application

```bash
streamlit run app/main.py
```

Application will be available at:

```text
http://localhost:8501
```

---

# Screenshots

## Dashboard

Add screenshot:

```markdown
![Dashboard](screenshots/dashboard.png)
```

---

## AI Chat

```markdown
![AI Chat](screenshots/ai-chat.png)
```

---

## Forecasting

```markdown
![Forecasting](screenshots/forecasting.png)
```

---

## Anomaly Detection

```markdown
![Anomaly Detection](screenshots/anomaly-detection.png)
```

---

## Business Insights

```markdown
![Business Insights](screenshots/business-insights.png)
```

---

# Example Business Questions

The AI Business Analyst can answer:

- Which region generates the highest revenue?
- What category has the highest profit?
- Which products contribute most to profitability?
- What business recommendations do you have?
- Summarize this dataset.
- Which regions are underperforming?
- What are the key business risks?

---

# Key Achievements

- Built an end-to-end AI-powered Business Analytics Platform.
- Implemented Retrieval-Augmented Generation (RAG).
- Integrated Google Gemini for conversational analytics.
- Developed forecasting and anomaly detection modules.
- Created executive-level business insight generation.
- Built interactive dashboards using Streamlit and Plotly.
- Optimized semantic search using FAISS Vector Database.

---

# Future Enhancements

- Multi-file dataset support
- PDF Executive Reports
- Automated PowerPoint Generation
- Advanced Time Series Models
- Customer Segmentation
- Demand Forecasting
- Cloud Deployment
- User Authentication
- Role-Based Access Control
- Real-Time Analytics

---

# Resume Highlights

Built an AI-powered Business Analytics Platform integrating Data Analysis, Machine Learning, Forecasting, Anomaly Detection, and Retrieval-Augmented Generation (RAG) using Gemini, FAISS, and Sentence Transformers.

Developed interactive dashboards, predictive analytics modules, and conversational AI capabilities to automate business intelligence workflows and generate executive-level business insights.

---

# Author

## Rithwik Nambiar
---

# License

This project is developed for educational, portfolio, and research purposes.
