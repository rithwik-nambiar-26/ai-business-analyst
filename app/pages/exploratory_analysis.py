import sys
from pathlib import Path

import pandas as pd
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

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Exploratory Analysis",
    layout="wide"
)

st.title(
    "📊 Exploratory Data Analysis"
)

# =====================================
# LOAD DATA
# =====================================

df = DataManager.get_data()

if df is None:

    st.warning(
        "Please upload and select a dataset first."
    )

    st.stop()

# =====================================
# EDA ENGINE
# =====================================

eda = ExploratoryAnalysis(df)

eda_report = (
    eda.generate_eda_report()
)

# =====================================
# DATASET SUMMARY
# =====================================

st.header(
    "Dataset Summary"
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

# =====================================
# NUMERIC ANALYSIS
# =====================================

st.header(
    "Numeric Analysis"
)

numeric_summary = (
    eda_report.get(
        "numeric_summary",
        {}
    )
)

if numeric_summary:

    numeric_df = pd.DataFrame(
        numeric_summary
    ).T

    st.dataframe(
        numeric_df,
        use_container_width=True
    )

else:

    st.info(
        "No numeric columns found."
    )

# =====================================
# CATEGORICAL ANALYSIS
# =====================================

st.header(
    "Categorical Analysis"
)

categorical_summary = (
    eda_report.get(
        "categorical_summary",
        {}
    )
)

if categorical_summary:

    for column, values in (
        categorical_summary.items()
    ):

        st.subheader(
            column
        )

        category_df = pd.DataFrame(

            list(values.items()),

            columns=[
                "Value",
                "Count"
            ]
        )

        st.dataframe(
            category_df,
            use_container_width=True
        )

else:

    st.info(
        "No categorical columns found."
    )

# =====================================
# DATE ANALYSIS
# =====================================

st.header(
    "Date Analysis"
)

date_summary = (
    eda_report.get(
        "date_summary",
        {}
    )
)

if date_summary:

    st.json(
        date_summary
    )

else:

    st.info(
        "No date columns found."
    )

# =====================================
# CORRELATION ANALYSIS
# =====================================

st.header(
    "Correlation Analysis"
)

correlations = (
    eda_report.get(
        "correlation_analysis",
        {}
    )
)

if correlations:

    correlation_df = pd.DataFrame(

        list(
            correlations.items()
        ),

        columns=[
            "Column Pair",
            "Correlation"
        ]
    )

    correlation_df = (
        correlation_df
        .sort_values(
            by="Correlation",
            ascending=False
        )
    )

    st.dataframe(
        correlation_df,
        use_container_width=True
    )

else:

    st.info(
        "Not enough numeric columns for correlation analysis."
    )

# =====================================
# OUTLIER ANALYSIS
# =====================================

st.header(
    "Outlier Analysis"
)

outliers = (
    eda_report.get(
        "outlier_analysis",
        {}
    )
)

if outliers:

    outlier_df = pd.DataFrame(
        outliers
    ).T

    st.dataframe(
        outlier_df,
        use_container_width=True
    )

else:

    st.info(
        "No outlier analysis available."
    )

# =====================================
# DATA PREVIEW
# =====================================

st.header(
    "Dataset Preview"
)

st.dataframe(
    df.head(100),
    use_container_width=True
)