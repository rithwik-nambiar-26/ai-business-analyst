import sys
from pathlib import Path

import streamlit as st

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.profiling.data_profiler import DataProfiler
from src.preprocessing.data_cleaner import DataCleaner
from src.eda.exploratory_analysis import ExploratoryAnalysis
from src.insights.insight_generator import InsightGenerator
from src.insights.business_insight_engine import BusinessInsightEngine

from app.utils.data_manager import DataManager


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Universal AI Data Analyst",
    page_icon="���📊",
    layout="wide"
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("���📊 Universal AI Data Analyst")

st.markdown(
    """
    Upload, manage and analyze multiple datasets.

    Features:

    • Dataset Intelligence
    • Dynamic EDA
    • AI Insights
    • Forecasting
    • Anomaly Detection
    • AI Chat
    • Reporting
    """
)

st.markdown("---")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("���📁 Dataset Management")

uploaded_file = st.sidebar.file_uploader(
    "Upload Dataset",
    type=[
        "csv",
        "xlsx",
        "xls"
    ]
)

# --------------------------------------------------
# DATASET UPLOAD
# --------------------------------------------------

if uploaded_file:

    df = DataManager.save_uploaded_data(
        uploaded_file
    )

    st.sidebar.success(
        f"Uploaded: {uploaded_file.name}"
    )

# --------------------------------------------------
# DATASET SELECTOR
# --------------------------------------------------

available_datasets = (
    DataManager.get_available_datasets()
)

dataset_names = [
    dataset["dataset_name"]
    for dataset in available_datasets
]

if dataset_names:

    current_dataset = (
        DataManager.get_active_dataset_name()
    )

    if (
        current_dataset
        not in dataset_names
    ):

        current_dataset = dataset_names[0]

    selected_dataset = st.sidebar.selectbox(
        "Select Dataset",
        options=dataset_names,
        index=dataset_names.index(
            current_dataset
        )
    )

    if (
        selected_dataset
        != current_dataset
    ):

        DataManager.load_dataset_by_name(
            selected_dataset
        )

        st.rerun()

# --------------------------------------------------
# LOAD ACTIVE DATASET
# --------------------------------------------------

df = DataManager.get_data()

if df is None:

    st.info(
        """
        �� 👋 Welcome to Universal AI Data Analyst

        Upload a dataset to begin analysis.

        Supported:

        • Sales
        • Finance
        • Banking
        • Telecom
        • HR
        • Healthcare
        • Marketing
        • Generic CSV Files
        """
    )

    st.stop()

# --------------------------------------------------
# LOAD METADATA
# --------------------------------------------------

schema_metadata = (
    DataManager.get_schema_metadata()
)

dataset_summary = (
    DataManager.get_dataset_summary()
)

dataset_fingerprint = (
    DataManager.get_dataset_fingerprint()
)

dataset_intelligence = (
    DataManager.get_dataset_intelligence()
)

# --------------------------------------------------
# CURRENT DATASET PANEL
# --------------------------------------------------

active_dataset = (
    DataManager.get_active_dataset_name()
)

if active_dataset:

    st.sidebar.markdown("---")

    st.sidebar.subheader(
        "Active Dataset"
    )

    st.sidebar.success(
        active_dataset
    )

    if dataset_intelligence:

        st.sidebar.write(
            f"Type: {dataset_intelligence.get('dataset_type', 'Generic').title()}"
        )

        st.sidebar.write(
            f"Entity: {dataset_intelligence.get('entity_type', 'Records').title()}"
        )

        st.sidebar.write(
            f"Rows: {dataset_summary.get('row_count', 0):,}"
        )

        st.sidebar.write(
            f"Columns: {dataset_summary.get('column_count', 0)}"
        )

        # Show description
        st.sidebar.caption(dataset_intelligence.get('description', ''))

# --------------------------------------------------
# PROCESSING PIPELINE
# --------------------------------------------------

profiler = DataProfiler(df)

profile_report = (
    profiler.generate_profile()
)

cleaner = DataCleaner(df)

cleaning_report = (
    cleaner.generate_cleaning_report()
)

eda = ExploratoryAnalysis(df)

eda_report = (
    eda.generate_eda_report()
)

# Generate basic insights for context building
basic_insight_generator = InsightGenerator(
    eda_report
)
basic_insights = basic_insight_generator.generate_all_insights()

# Generate business insights for display
business_insight_engine = BusinessInsightEngine(eda_report)
business_insights = business_insight_engine.generate_all_insights()

# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

st.header("���📁 Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Rows",
        profile_report["rows"]
    )

with col2:

    st.metric(
        "Columns",
        profile_report["columns"]
    )

with col3:

    st.metric(
        "Memory (MB)",
        profile_report[
            "memory_usage_mb"
        ]
    )

with col4:

    st.metric(
        "Duplicate Rows",
        cleaning_report[
            "duplicate_rows"
        ]
    )

# Dataset description
if dataset_intelligence:
    st.info(dataset_intelligence.get('description', ''))

# --------------------------------------------------
# DATASET UNDERSTANDING
# --------------------------------------------------

st.markdown("---")

st.header(
    "Dataset Intelligence"
)

if dataset_intelligence:

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Dataset Type:** {dataset_intelligence.get('dataset_type', 'Generic').title()}"
        )

        st.write(
            f"**Primary Entity:** {dataset_intelligence.get('entity_type', 'Records').title()}"
        )

        st.write(
            f"**Rows:** {dataset_summary.get('row_count', 0):,}"
        )

        st.write(
            f"**Columns:** {dataset_summary.get('column_count', 0)}"
        )

    with col2:

        st.write(
            "**Description**"
        )
        st.info(dataset_intelligence.get('description', 'No description available'))

        st.write(
            "**Key Features Detected**"
        )
        features = []
        if dataset_intelligence.get('important_metrics'):
            features.append(f"{len(dataset_intelligence['important_metrics'])} key measurements")
        if dataset_intelligence.get('important_dimensions'):
            features.append(f"{len(dataset_intelligence['important_dimensions'])} grouping categories")
        if dataset_intelligence.get('time_column'):
            features.append("Time series capability")
        if dataset_intelligence.get('available_analyses'):
            features.append(f"{len(dataset_intelligence['available_analyses'])} analysis types available")

        for feature in features:
            st.write(f"• {feature}")
else:
    # Fallback to original dataset summary if intelligence not available
    if dataset_summary:

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Rows:** {dataset_summary.get('row_count', 0):,}"
            )

            st.write(
                f"**Columns:** {dataset_summary.get('column_count', 0)}"
            )

            st.write(
                "**Capabilities**"
            )

            st.json(
                dataset_summary.get(
                    "capabilities",
                    {}
                )
            )

        with col2:

            st.write(
                "**Candidate Metrics**"
            )

            st.write(
                dataset_summary.get(
                    "candidate_metrics",
                    []
                )
            )

            st.write(
                "**Candidate Dimensions**"
            )

            st.write(
                dataset_summary.get(
                    "candidate_dimensions",
                    []
                )
            )

# --------------------------------------------------
# SCHEMA ANALYSIS
# --------------------------------------------------

st.markdown("---")

st.header("���🔍 Schema Analysis")

if schema_metadata:

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            "**Numeric Columns**"
        )

        st.write(
            schema_metadata.get(
                "numeric_columns",
                []
            )
        )

        st.write(
            "**Date Columns**"
        )

        st.write(
            schema_metadata.get(
                "date_columns",
                []
            )
        )

    with col2:

        st.write(
            "**Categorical Columns**"
        )

        st.write(
            schema_metadata.get(
                "categorical_columns",
                []
            )
        )

        st.write(
            "**Boolean Columns**"
        )

        st.write(
            schema_metadata.get(
                "boolean_columns",
                []
            )
        )

    with col3:

        st.write(
            "**Text Columns**"
        )

        st.write(
            schema_metadata.get(
                "text_columns",
                []
            )
        )

        st.write(
            "**ID Columns**"
        )

        st.write(
            schema_metadata.get(
                "id_columns",
                []
            )
        )

# --------------------------------------------------
# DATA QUALITY
# --------------------------------------------------

st.markdown("---")

st.header("���🧹 Data Quality")

col1, col2 = st.columns(2)

with col1:

    total_missing = sum(
        cleaning_report[
            "missing_values"
        ].values()
    )

    st.metric(
        "Missing Values",
        total_missing
    )

with col2:

    st.metric(
        "Duplicate Rows",
        cleaning_report[
            "duplicate_rows"
        ]
    )

# --------------------------------------------------
# EDA
# --------------------------------------------------

st.markdown("---")

st.header(
    "���📈 Exploratory Data Analysis"
)

st.subheader(
    "Dataset Summary"
)

st.json(
    eda_report[
        "dataset_summary"
    ]
)

st.subheader(
    "Numeric Summary"
)

st.json(
    eda_report[
        "numeric_summary"
    ]
)

st.subheader(
    "Date Summary"
)

st.json(
    eda_report[
        "date_summary"
    ]
)

st.subheader(
    "Correlation Analysis"
)

st.json(
    eda_report[
        "correlation_analysis"
    ]
)

st.subheader(
    "Outlier Analysis"
)

st.json(
    eda_report[
        "outlier_analysis"
    ]
)

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------

st.markdown("---")

st.header(
    "���🤖 AI Insights"
)

# Display business insights with categorization
if business_insights:
    # Group insights by category
    insights_by_category = {}
    for insight in business_insights:
        category = insight.category
        if category not in insights_by_category:
            insights_by_category[category] = []
        insights_by_category[category].append(insight)

    # Display insights by category
    category_icons = {
        "performance": "���📈",
        "risk": "��⚠��️",
        "opportunity": "���💡",
        "trend": "���🔮",
        "data_quality": "���🧹"
    }

    for category, category_insights in insights_by_category.items():
        icon = category_icons.get(category, "���📊")
        with st.expander(f"{icon} {category.title()} Insights ({len(category_insights)})", expanded=True):
            for index, insight in enumerate(category_insights, start=1):
                st.info(f"**Insight {index}:** {insight.insight}")
                if insight.suggested_action:
                    st.caption(f"���💡 Suggested Action: {insight.suggested_action}")
else:
    # Fallback to basic insights if no business insights generated
    for index, insight in enumerate(
        basic_insights,
        start=1
    ):
        st.success(
            f"Insight {index}: {insight}"
        )

# --------------------------------------------------
# QUESTIONS
# --------------------------------------------------

if dataset_summary:

    st.markdown("---")

    st.header(
        "���💡 Suggested Questions"
    )

    for question in dataset_summary.get(
        "suggested_questions",
        []
    ):

        st.info(question)

# --------------------------------------------------
# DATASET FINGERPRINT
# --------------------------------------------------

st.markdown("---")

st.header(
    "���🔐 Dataset Fingerprint"
)

st.code(
    dataset_fingerprint
)

# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------

st.markdown("---")

st.header(
    "���📄 Dataset Preview"
)

st.dataframe(
    df.head(100),
    width="stretch"
)