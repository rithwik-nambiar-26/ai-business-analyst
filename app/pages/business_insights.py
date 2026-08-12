import sys
from pathlib import Path

import streamlit as st

project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

sys.path.append(
    str(project_root)
)

from app.utils.data_manager import (
    DataManager
)

from src.eda.exploratory_analysis import (
    ExploratoryAnalysis
)

from src.insights.insight_generator import (
    InsightGenerator
)
from src.insights.business_insight_engine import (
    BusinessInsightEngine
)

st.set_page_config(
    page_title="Business Insights",
    layout="wide"
)

st.title(
    "���������📊 Business Insights"
)

# =====================================
# LOAD DATASET
# =====================================

df = DataManager.get_data()

if df is None:

    st.warning(
        "Please upload and select a dataset first."
    )

    st.stop()

# =====================================
# EDA
# =====================================

eda = ExploratoryAnalysis(
    df
)

eda_report = (
    eda.generate_eda_report()
)

# Generate basic insights for compatibility
basic_insight_generator = (
    InsightGenerator(
        eda_report
    )
)
basic_insights = basic_insight_generator.generate_all_insights()

# Generate business insights for display
business_insight_engine = BusinessInsightEngine(eda_report)
business_insights = business_insight_engine.generate_all_insights()

# =====================================
# DATASET OVERVIEW
# =====================================

st.header(
    "Dataset Overview"
)

summary = (
    eda_report.get(
        "dataset_summary",
        {}
    )
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Rows",
        summary.get(
            "rows",
            0
        )
    )

with col2:

    st.metric(
        "Columns",
        summary.get(
            "columns",
            0
        )
    )

with col3:

    st.metric(
        "Missing Values",
        summary.get(
            "missing_values",
            0
        )
    )

with col4:

    st.metric(
        "Duplicate Rows",
        summary.get(
            "duplicate_rows",
            0
        )
    )

st.divider()

# =====================================
# EXECUTIVE INSIGHTS
# =====================================

st.header(
    "Executive Insights"
)

# Get dataset intelligence for context
dataset_intelligence = DataManager.get_dataset_intelligence()
entity_name = dataset_intelligence.get('entity_name_singular', 'record') if dataset_intelligence else 'record'
entity_type = dataset_intelligence.get('entity_type', 'records') if dataset_intelligence else 'records'

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
        "performance": "���������📈",
        "risk": "������⚠������️",
        "opportunity": "���������💡",
        "trend": "���������🔮",
        "data_quality": "���������🧹"
    }

    for category, category_insights in insights_by_category.items():
        icon = category_icons.get(category, "���������📊")
        with st.expander(f"{icon} {category.title()} Insights ({len(category_insights)})", expanded=True):
            for index, insight in enumerate(category_insights, start=1):
                st.info(f"**Insight {index}:** {insight.insight}")
                if insight.suggested_action:
                    st.caption(f"���������💡 Suggested Action: {insight.suggested_action}")
else:
    # Fallback to basic insights if no business insights generated
    for insight in basic_insights:
        st.success(
            insight
        )

st.divider()

# =====================================
# NUMERIC FINDINGS
# =====================================

numeric_summary = (
    eda_report.get(
        "numeric_summary",
        {}
    )
)

if numeric_summary:

    st.header(
        "Numeric Findings"
    )

    for column, stats in (
        numeric_summary.items()
    ):

        with st.expander(
            column
        ):

            st.write(
                stats
            )

st.divider()

# =====================================
# CATEGORICAL FINDINGS
# =====================================

categorical_summary = (
    eda_report.get(
        "categorical_summary",
        {}
    )
)

if categorical_summary:

    st.header(
        "Categorical Findings"
    )

    for column, values in (
        categorical_summary.items()
    ):

        with st.expander(
            column
        ):

            st.write(
                values
            )

st.divider()

# =====================================
# CORRELATIONS
# =====================================

correlations = (
    eda_report.get(
        "correlation_analysis",
        {}
    )
)

if correlations:

    st.header(
        "Strong Relationships"
    )

    sorted_correlations = sorted(
        correlations.items(),
        key=lambda x: abs(
            x[1]
        ),
        reverse=True
    )

    for pair, value in (
        sorted_correlations[:10]
    ):

        st.info(
            f"{pair} → {value}"
        )

st.divider()

# =====================================
# OUTLIERS
# =====================================

outliers = (
    eda_report.get(
        "outlier_analysis",
        {}
    )
)

if outliers:

    st.header(
        "Outlier Analysis"
    )

    for column, details in (
        outliers.items()
    ):

        st.warning(
            f"{column}: "
            f"{details['outlier_count']} "
            f"outliers "
            f"({details['outlier_percentage']}%)"
        )

st.divider()

# =====================================
# DATA QUALITY
# =====================================

missing = (
    eda_report.get(
        "missing_value_analysis",
        {}
    )
)

st.header(
    "Data Quality Findings"
)

if missing:

    for column, count in (
        missing.items()
    ):

        st.warning(
            f"{column}: {count} missing values"
        )

else:

    st.success(
        "No missing values detected."
    )