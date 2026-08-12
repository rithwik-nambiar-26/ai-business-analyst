import sys
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

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

from src.kpi.kpi_engine import (
    identify_kpi_columns
)

from src.forecasting.forecast_engine import (
    generate_forecast
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Trend Forecasting",
    page_icon="🔮",
    layout="wide"
)

st.title(
    "🔮 Predictive Forecasting Engine"
)

st.markdown("---")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = DataManager.get_data()

if df is None:

    st.warning(
        "Please upload and select a dataset first."
    )

    st.stop()

# --------------------------------------------------
# CAPABILITY CHECK
# --------------------------------------------------

dataset_summary = (
    DataManager.get_dataset_summary()
)

capabilities = (
    dataset_summary.get(
        "capabilities",
        {}
    )
)

if not capabilities.get(
    "forecasting",
    False
):

    st.info(
        "This dataset does not support forecasting."
    )

    st.stop()

# --------------------------------------------------
# KPI DETECTION
# --------------------------------------------------

kpi_cols = identify_kpi_columns(
    df
)

date_col = kpi_cols[
    "date_column"
]

metric_cols = kpi_cols[
    "metric_columns"
]

# --------------------------------------------------
# VALIDATION
# --------------------------------------------------

if not date_col:

    st.warning(
        "No date column detected."
    )

    st.stop()

if not metric_cols:

    st.warning(
        "No numeric metrics detected."
    )

    st.stop()

# --------------------------------------------------
# CONFIG PANEL
# --------------------------------------------------

left_col, right_col = st.columns(
    [1, 3]
)

with left_col:

    st.subheader(
        "Forecast Configuration"
    )

    target_metric = st.selectbox(
        "Target Metric",
        metric_cols
    )

    frequency = st.selectbox(
        "Forecast Frequency",
        [
            ("Monthly", "M"),
            ("Weekly", "W"),
            ("Daily", "D")
        ],
        format_func=lambda x: x[0]
    )

    horizon = st.slider(
        "Forecast Horizon",
        min_value=3,
        max_value=24,
        value=6
    )

    run_forecast = st.button(
        "Generate Forecast"
    )

# --------------------------------------------------
# FORECAST OUTPUT
# --------------------------------------------------

with right_col:

    st.subheader(
        "Forecast Results"
    )

    if run_forecast:

        with st.spinner(
            "Generating Forecast..."
        ):

            forecast_df, status = (
                generate_forecast(
                    df=df,
                    date_col=date_col,
                    target_col=target_metric,
                    horizon=horizon,
                    freq=frequency[1]
                )
            )

        if forecast_df.empty:

            st.error(
                status
            )

        else:

            st.success(
                status
            )

            history = forecast_df[
                forecast_df["Is_Forecast"]
                == False
            ]

            future = forecast_df[
                forecast_df["Is_Forecast"]
                == True
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=history["Date"],
                    y=history["Actual"],
                    mode="lines+markers",
                    name="Actual"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=history["Date"],
                    y=history["Forecast"],
                    mode="lines",
                    name="Fitted"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=future["Date"],
                    y=future["Forecast"],
                    mode="lines+markers",
                    name="Forecast"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=future["Date"],
                    y=future["Upper_CI"],
                    line=dict(width=0),
                    showlegend=False
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=future["Date"],
                    y=future["Lower_CI"],
                    fill="tonexty",
                    line=dict(width=0),
                    name="95% Confidence Interval"
                )
            )

            fig.update_layout(

                title=f"{target_metric} Forecast",

                xaxis_title="Date",

                yaxis_title=target_metric,

                hovermode="x unified"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader(
                "Forecast Table"
            )

            st.dataframe(
                future[
                    [
                        "Date",
                        "Forecast",
                        "Lower_CI",
                        "Upper_CI"
                    ]
                ],
                use_container_width=True
            )

    else:

        st.info(
            "Select a metric and click Generate Forecast."
        )