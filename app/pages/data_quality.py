import sys
from pathlib import Path

import pandas as pd
import streamlit as st

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from app.utils.data_manager import DataManager
from src.profiling.data_profiler import DataProfiler
from src.preprocessing.data_cleaner import DataCleaner


st.set_page_config(
    page_title="Data Quality",
    layout="wide"
)

st.title("Data Quality Report")

df = DataManager.get_data()

if df is None:

    st.warning(
        "Please upload and select a dataset first."
    )

    st.stop()

profiler = DataProfiler(df)
profile = profiler.generate_profile()

cleaner = DataCleaner(df)
quality_report = cleaner.generate_cleaning_report()

# Summary Section

st.header("Dataset Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Rows",
        profile["rows"]
    )

with col2:
    st.metric(
        "Columns",
        profile["columns"]
    )

with col3:
    total_missing = sum(
        quality_report["missing_values"].values()
    )

    st.metric(
        "Missing Values",
        total_missing
    )

with col4:
    st.metric(
        "Duplicate Rows",
        quality_report["duplicate_rows"]
    )

st.markdown("---")

# Data Types

st.header("Column Data Types")

dtype_df = pd.DataFrame(
    list(profile["data_types"].items()),
    columns=["Column", "Data Type"]
)

st.dataframe(
    dtype_df,
    use_container_width=True
)

# Missing Values

st.header("Missing Values")

missing_df = pd.DataFrame(
    list(
        quality_report["missing_values"].items()
    ),
    columns=["Column", "Missing Values"]
)

st.dataframe(
    missing_df,
    use_container_width=True
)

# Date Validation

st.header("Date Validation")

date_df = pd.DataFrame(
    list(
        quality_report["invalid_dates"].items()
    ),
    columns=[
        "Date Column",
        "Invalid Records"
    ]
)

st.dataframe(
    date_df,
    use_container_width=True
)

st.markdown("---")

# Quality Status

st.header("Quality Status")

if total_missing == 0:
    st.success(
        "No missing values found."
    )

if quality_report["duplicate_rows"] == 0:
    st.success(
        "No duplicate records found."
    )

if all(
    value == 0
    for value in quality_report[
        "invalid_dates"
    ].values()
):
    st.success(
        "All date fields are valid."
    )