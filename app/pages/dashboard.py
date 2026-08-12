import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

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
    page_title="Dashboard",
    layout="wide"
)

st.title(
    "���������📊 Dataset Intelligence Dashboard"
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

dataset_summary = (
    DataManager.get_dataset_summary()
)
dataset_intelligence = DataManager.get_dataset_intelligence()

eda = ExploratoryAnalysis(
    df
)

eda_report = (
    eda.generate_eda_report()
)

# =====================================
# DATASET OVERVIEW
# =====================================

st.header(
    "Dataset Overview"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Rows",
        dataset_summary.get(
            "row_count",
            0
        )
    )

with col2:

    st.metric(
        "Columns",
        dataset_summary.get(
            "column_count",
            0
        )
    )

with col3:

    st.metric(
        "Missing Values",
        sum(
            dataset_summary.get(
                "missing_values",
                {}
            ).values()
        )
    )

with col4:

    st.metric(
        "Duplicate Rows",
        dataset_summary.get(
            "duplicate_rows",
            0
        )
    )

st.divider()

# =====================================
# KEY METRICS
# =====================================

st.header(
    "Key Metrics"
)

# Get KPIs from dataset intelligence
if dataset_intelligence and dataset_intelligence.get('kpis'):
    kpis = dataset_intelligence['kpis']

    # Limit to 4 columns
    metric_columns = st.columns(min(4, len(kpis)))

    for idx, kpi in enumerate(kpis[:4]):
        column = kpi['column']
        display_name = kpi['display_name']
        calc_type = kpi['calculation']

        try:
            if calc_type == 'sum':
                value = round(float(df[column].sum()), 2)
            else:  # average
                value = round(float(df[column].mean()), 2)

            # Format based on KPI specification
            format_type = kpi.get('format', 'number')
            if format_type == 'currency':
                formatted_value = f"${value:,.2f}"
            else:
                formatted_value = f"{value:,.2f}"

            with metric_columns[idx]:
                st.metric(
                    display_name,
                    formatted_value
                )
        except Exception:
            continue
else:
    # Fallback to original logic
    candidate_metrics = (
        dataset_summary.get(
            "candidate_metrics",
            []
        )
    )

    if candidate_metrics:

        metric_columns = st.columns(
            min(
                4,
                len(candidate_metrics)
            )
        )

        for idx, metric in enumerate(
            candidate_metrics[:4]
        ):

            try:

                value = round(
                    float(
                        df[metric].mean()
                    ),
                    2
                )

                with metric_columns[idx]:

                    st.metric(
                        metric,
                        value
                    )

            except Exception:

                continue

    else:

        st.info(
            "No candidate metrics detected."
        )

st.divider()

# =====================================
# METRIC EXPLORER
# =====================================

st.header(
    "Metric Explorer"
)

candidate_metrics = (
    dataset_summary.get(
        "candidate_metrics",
        []
    )
)
candidate_dimensions = (
    dataset_summary.get(
        "candidate_dimensions",
        []
    )
)

if (

    len(candidate_metrics) > 0
    and
    len(candidate_dimensions) > 0

):

    col1, col2 = st.columns(2)

    with col1:

        selected_metric = (
            st.selectbox(
                "Select Metric",
                candidate_metrics
            )
        )

    with col2:

        selected_dimension = (
            st.selectbox(
                "Select Dimension",
                candidate_dimensions
            )
        )

    try:

        chart_df = (
            df.groupby(
                selected_dimension
            )[selected_metric]

            .mean()

            .reset_index()

            .sort_values(
                selected_metric,
                ascending=False
            )
        )

        if not chart_df.empty:

            fig = px.bar(
                chart_df,
                x=selected_dimension,
                y=selected_metric,
                title=(
                    f"{selected_metric}"
                    f" by "
                    f"{selected_dimension}"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No data available for chart."
            )

    except Exception as e:

        st.warning(
            f"Unable to build chart: {e}"
        )

else:

    st.info(
        "Metric Explorer requires both numeric metrics and categorical dimensions."
    )

st.divider()

# =====================================
# CORRELATION HIGHLIGHTS
# =====================================

st.header(
    "Correlation Highlights"
)

correlations = (
    eda_report.get(
        "correlation_analysis",
        {}
    )
)

if correlations:

    valid_correlations = {

        pair: value

        for pair, value in correlations.items()

        if pd.notna(value)

    }

    if valid_correlations:

        top_correlations = sorted(

            valid_correlations.items(),

            key=lambda x: abs(
                x[1]
            ),

            reverse=True

        )[:5]

        for pair, value in (
            top_correlations
        ):

            st.info(
                f"{pair} → {value}"
            )

    else:

        st.info(
            "No valid correlations detected."
        )

else:

    st.info(
        "No correlation analysis available."
    )

st.divider()

# =====================================
# OUTLIER SUMMARY
# =====================================

st.header(
    "Outlier Summary"
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

    outlier_df = (
        outlier_df
        .sort_values(
            by="outlier_percentage",
            ascending=False
        )
    )

    st.dataframe(
        outlier_df,
        use_container_width=True
    )

else:

    st.info(
        "No outlier analysis available."
    )

st.divider()

# =====================================
# DATA PREVIEW
# =====================================

st.header(
    "Dataset Preview"
)

st.dataframe(
    df.head(20),
    use_container_width=True
)