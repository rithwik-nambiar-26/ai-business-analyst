import hashlib
from datetime import datetime

import streamlit as st

from src.ingestion.data_loader import DataLoader
from src.schema.dataset_understanding import understand_dataset
from src.schema.schema_analyzer import analyze_schema
from src.dataset_intelligence import get_dataset_intelligence

from src.dataset_manager.dataset_storage import (
    DatasetStorage
)

from src.dataset_manager.dataset_registry import (
    DatasetRegistry
)

from src.dataset_manager.dataset_selector import (
    DatasetSelector
)


class DataManager:

    @staticmethod
    def save_uploaded_data(uploaded_file):

        if uploaded_file is None:
            return None

        saved_path = (
            DatasetStorage.save_uploaded_file(
                uploaded_file
            )
        )

        df = DataLoader.load_data(
            saved_path
        )

        schema_metadata = analyze_schema(
            df
        )

        dataset_summary = understand_dataset(
            df,
            schema_metadata
        )

        dataset_fingerprint = (
            DataManager.generate_dataset_fingerprint(
                df
            )
        )

        dataset_metadata = {

            "dataset_name":
                uploaded_file.name,

            "dataset_path":
                str(saved_path),

            "dataset_type":
                dataset_summary.get(
                    "dataset_type",
                    "Generic"
                ),

            "rows":
                int(len(df)),

            "columns":
                int(len(df.columns)),

            "upload_time":
                datetime.now()
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "fingerprint":
                dataset_fingerprint
        }

        DatasetRegistry.register_dataset(
            dataset_metadata
        )

        DatasetSelector.set_active_dataset(
            uploaded_file.name
        )

        DataManager.store_dataset(
            df
        )

        return df

    @staticmethod
    def get_data():

        if "df" in st.session_state:

            return st.session_state[
                "df"
            ]

        active_dataset = (
            DatasetSelector
            .get_active_dataset()
        )

        if active_dataset:

            dataset_info = (
                DatasetRegistry
                .get_dataset(
                    active_dataset
                )
            )

            if dataset_info:

                df = DataLoader.load_data(
                    dataset_info[
                        "dataset_path"
                    ]
                )

                DataManager.store_dataset(
                    df
                )

                return df

        return None

    @staticmethod
    def load_dataset_by_name(
        dataset_name
    ):

        dataset_info = (
            DatasetRegistry
            .get_dataset(
                dataset_name
            )
        )

        if not dataset_info:

            return None

        df = DataLoader.load_data(
            dataset_info[
                "dataset_path"
            ]
        )

        DatasetSelector.set_active_dataset(
            dataset_name
        )

        DataManager.store_dataset(
            df
        )

        return df

    @staticmethod
    def get_available_datasets():

        return (
            DatasetRegistry
            .get_all_datasets()
        )

    @staticmethod
    def get_active_dataset_name():

        return (
            DatasetSelector
            .get_active_dataset()
        )

    @staticmethod
    def store_dataset(df):

        schema_metadata = analyze_schema(
            df
        )

        dataset_summary = understand_dataset(
            df,
            schema_metadata
        )

        # Generate dataset intelligence
        dataset_intelligence = get_dataset_intelligence(df)
        dataset_intelligence_dict = {
            'dataset_type': dataset_intelligence.dataset_type,
            'entity_type': dataset_intelligence.entity_type,
            'entity_name_singular': dataset_intelligence.entity_name_singular,
            'description': dataset_intelligence.description,
            'column_display_names': dataset_intelligence.column_display_names,
            'column_descriptions': dataset_intelligence.column_descriptions,
            'important_metrics': dataset_intelligence.important_metrics,
            'important_dimensions': dataset_intelligence.important_dimensions,
            'time_column': dataset_intelligence.time_column,
            'available_analyses': dataset_intelligence.available_analyses,
            'recommended_analyses': dataset_intelligence.recommended_analyses,
            'page_names': dataset_intelligence.page_names,
            'kpis': dataset_intelligence.kpis,
            'chart_suggestions': dataset_intelligence.chart_suggestions,
            'terminology': dataset_intelligence.terminology,
            'suggested_questions': dataset_intelligence.suggested_questions,
            'suggested_actions': dataset_intelligence.suggested_actions
        }

        dataset_fingerprint = (
            DataManager.generate_dataset_fingerprint(
                df
            )
        )

        st.session_state[
            "df"
        ] = df

        st.session_state[
            "uploaded_df"
        ] = df

        st.session_state[
            "schema_metadata"
        ] = schema_metadata

        st.session_state[
            "dataset_summary"
        ] = dataset_summary

        st.session_state[
            "dataset_intelligence"
        ] = dataset_intelligence_dict

        st.session_state[
            "dataset_fingerprint"
        ] = dataset_fingerprint

        return {
            "df": df,
            "schema_metadata": schema_metadata,
            "dataset_summary": dataset_summary,
            "dataset_intelligence": dataset_intelligence_dict,
            "dataset_fingerprint": dataset_fingerprint,
        }

    @staticmethod
    def get_schema_metadata():

        return st.session_state.get(
            "schema_metadata"
        )

    @staticmethod
    def get_dataset_summary():

        return st.session_state.get(
            "dataset_summary"
        )

    @staticmethod
    def get_dataset_fingerprint():

        return st.session_state.get(
            "dataset_fingerprint"
        )

    @staticmethod
    def get_dataset_intelligence():
        return st.session_state.get(
            "dataset_intelligence"
        )

    @staticmethod
    def generate_dataset_fingerprint(
        df
    ):

        dataframe_copy = df.copy()

        payload = dataframe_copy.to_csv(
            index=False,
            lineterminator="\n",
            date_format="%Y-%m-%dT%H:%M:%S.%f",
            na_rep="<NA>"
        )

        fingerprint = hashlib.sha256()

        fingerprint.update(
            "|".join(
                map(
                    str,
                    dataframe_copy.columns
                )
            ).encode(
                "utf-8"
            )
        )

        fingerprint.update(
            str(
                len(dataframe_copy)
            ).encode(
                "utf-8"
            )
        )

        fingerprint.update(
            payload.encode(
                "utf-8"
            )
        )

        return fingerprint.hexdigest()