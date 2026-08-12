from dataclasses import dataclass

import pandas as pd

from src.schema.schema_analyzer import (
    analyze_schema
)


@dataclass
class DatasetUnderstanding:

    df: pd.DataFrame

    schema_metadata: dict | None = None

    def summarize(self) -> dict:

        schema_metadata = (
            self.schema_metadata
            or
            analyze_schema(self.df)
        )

        candidate_metrics = (
            self._candidate_metrics(
                schema_metadata
            )
        )

        candidate_dimensions = (
            self._candidate_dimensions(
                schema_metadata
            )
        )

        capabilities = (
            self._capabilities(
                schema_metadata,
                candidate_metrics,
                candidate_dimensions
            )
        )

        return {

            "row_count":
                int(self.df.shape[0]),

            "column_count":
                int(self.df.shape[1]),

            "missing_values":
                self.df.isnull()
                .sum()
                .to_dict(),

            "duplicate_rows":
                int(
                    self.df
                    .duplicated()
                    .sum()
                ),

            "candidate_metrics":
                candidate_metrics,

            "candidate_dimensions":
                candidate_dimensions,

            "capabilities":
                capabilities,

            "suggested_questions":
                self._suggest_questions(
                    candidate_metrics,
                    candidate_dimensions,
                    schema_metadata
                )
        }

    # =====================================
    # NUMERIC CANDIDATES
    # =====================================

    def _candidate_metrics(
        self,
        schema_metadata
    ):

        excluded_columns = set(
            schema_metadata.get(
                "id_columns",
                []
            )
        )

        excluded_columns.update(
            schema_metadata.get(
                "boolean_columns",
                []
            )
        )

        return [

            column

            for column in
            schema_metadata.get(
                "numeric_columns",
                []
            )

            if column not in excluded_columns
        ]

    # =====================================
    # GROUPING CANDIDATES
    # =====================================

    def _candidate_dimensions(
        self,
        schema_metadata
    ):

        dimensions = []

        for key in [

            "categorical_columns",

            "boolean_columns",

            "date_columns"

        ]:

            for column in (
                schema_metadata.get(
                    key,
                    []
                )
            ):

                if column not in dimensions:

                    dimensions.append(
                        column
                    )

        return dimensions

    # =====================================
    # DATASET CAPABILITIES
    # =====================================

    def _capabilities(
        self,
        schema_metadata,
        candidate_metrics,
        candidate_dimensions
    ):

        return {

            "analytics":
                len(candidate_metrics) > 0,

            "group_analysis":
                len(candidate_dimensions) > 0,

            "record_lookup":
                len(
                    schema_metadata.get(
                        "id_columns",
                        []
                    )
                ) > 0,

            "forecasting":
                len(
                    schema_metadata.get(
                        "date_columns",
                        []
                    )
                ) > 0
                and
                len(candidate_metrics) > 0,

            "anomaly_detection":
                len(candidate_metrics) > 0,

            "correlation_analysis":
                len(candidate_metrics) >= 2
        }

    # =====================================
    # QUESTION SUGGESTIONS
    # =====================================

    def _suggest_questions(

        self,

        candidate_metrics,

        candidate_dimensions,

        schema_metadata

    ):

        questions = []

        if candidate_metrics:

            metric = (
                candidate_metrics[0]
            )

            questions.append(
                f"What is the overall summary of {metric}?"
            )

            if candidate_dimensions:

                dimension = (
                    candidate_dimensions[0]
                )

                questions.append(
                    f"How does {metric} vary by {dimension}?"
                )

        if len(candidate_metrics) >= 2:

            questions.append(
                "Which numeric columns are most strongly correlated?"
            )

        if (
            schema_metadata.get(
                "date_columns"
            )
            and
            candidate_metrics
        ):

            questions.append(
                f"What trend is visible over {schema_metadata['date_columns'][0]}?"
            )

        questions.append(
            "What are the most important patterns in this dataset?"
        )

        questions.append(
            "Are there missing values, duplicates, or outliers to review?"
        )

        return questions[:6]


def understand_dataset(

    df: pd.DataFrame,

    schema_metadata: dict | None = None

):

    return DatasetUnderstanding(
        df,
        schema_metadata
    ).summarize()