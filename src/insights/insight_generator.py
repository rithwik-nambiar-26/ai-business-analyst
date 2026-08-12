class InsightGenerator:

    def __init__(self, eda_report):
        self.eda_report = eda_report

    def generate_dataset_summary_insight(self):

        summary = self.eda_report.get(
            "dataset_summary",
            {}
        )

        rows = summary.get(
            "rows",
            0
        )

        columns = summary.get(
            "columns",
            0
        )

        duplicates = summary.get(
            "duplicate_rows",
            0
        )

        missing = summary.get(
            "missing_values",
            0
        )

        insight = (
            f"The dataset contains {rows:,} rows and "
            f"{columns} columns. "
            f"There are {missing:,} missing values and "
            f"{duplicates:,} duplicate records."
        )

        # Add business context
        if rows > 0:
            if missing == 0 and duplicates == 0:
                insight += " The dataset appears to be clean and ready for analysis."
            elif missing > rows * 0.1:  # More than 10% missing data
                insight += " Significant missing data may impact analysis reliability - consider data imputation or collection improvements."
            elif duplicates > rows * 0.05:  # More than 5% duplicates
                insight += " Notable duplicate records present - consider deduplication to ensure accurate counts."
            else:
                insight += " Dataset has minor data quality issues that should be reviewed before critical decisions."

        return insight

    def generate_numeric_insight(self):

        numeric_summary = self.eda_report.get(
            "numeric_summary",
            {}
        )

        if not numeric_summary:

            return (
                "No numeric columns were detected "
                "for statistical analysis."
            )

        insights = []

        for column, stats in list(
            numeric_summary.items()
        )[:3]:

            insight = (
                f"{column} has an average value of "
                f"{stats['mean']:,.2f} "
                f"with values ranging from "
                f"{stats['min']:,.2f} to "
                f"{stats['max']:,.2f}."
            )

            # Add business context based on statistics
            if stats['std'] > 0:
                cv = stats['std'] / stats['mean'] if stats['mean'] != 0 else float('inf')
                if cv < 0.5:
                    insight += " Values show relatively low variability, suggesting consistency."
                elif cv > 2.0:
                    insight += " Values show high variability, indicating potential volatility or diverse segments."
                elif stats.get('skew', 0) > 1:
                    insight += " Distribution is right-skewed, suggesting a few high-value outliers may be driving the average."
                elif stats.get('skew', 0) < -1:
                    insight += " Distribution is left-skewed, suggesting a few low-value outliers may be affecting the average."

            insights.append(insight)

        return " ".join(insights)

    def generate_categorical_insight(self):

        categorical_summary = self.eda_report.get(
            "categorical_summary",
            {}
        )

        if not categorical_summary:

            return (
                "No categorical columns were detected."
            )

        column = next(
            iter(categorical_summary)
        )

        values = categorical_summary[column]

        if not values:

            return (
                f"No category distribution "
                f"available for {column}."
            )

        top_value = max(
            values,
            key=values.get
        )

        count = values[top_value]
        total = sum(values.values())
        percentage = (count / total) * 100 if total > 0 else 0

        insight = (
            f"The most common value in "
            f"{column} is '{top_value}' "
            f"with {count:,} occurrences ({percentage:.1f}% of total)."
        )

        # Add business context
        if percentage > 80:
            insight += " Extreme concentration in one category may indicate limited diversity or data quality issues."
        elif percentage > 60:
            insight += " Strong dominance by one category suggests potential market concentration or segment focus."
        elif len(values) > 10:
            insight += " High category diversity suggests rich segmentation opportunities for targeted analysis."
        else:
            insight += " Moderate category distribution allows for meaningful comparative analysis."

        return insight

    def generate_date_insight(self):

        date_summary = self.eda_report.get(
            "date_summary",
            {}
        )

        if not date_summary:

            return (
                "No date columns were detected."
            )

        column = next(
            iter(date_summary)
        )

        details = date_summary[column]

        insight = (
            f"The dataset spans from "
            f"{details['start_date']} "
            f"to {details['end_date']} "
            f"based on {column}."
        )

        # Add business context
        try:
            from datetime import datetime
            start_date = datetime.strptime(details['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(details['end_date'], '%Y-%m-%d')
            duration_days = (end_date - start_date).days

            if duration_days < 30:
                insight += " Short time horizon may limit trend analysis but is suitable for operational reviews."
            elif duration_days < 365:
                insight += " Medium-term data enables seasonal pattern recognition and quarterly trend analysis."
            else:
                insight += " Long-term horizon supports year-over-year comparisons and trend identification for strategic planning."

            insight += f" Covers {duration_days} days of operational history."
        except:
            insight += " Temporal coverage enables time-based analysis and trend detection."

        return insight

    def generate_correlation_insight(self):

        correlations = self.eda_report.get(
            "correlation_analysis",
            {}
        )

        if not correlations:

            return (
                "Insufficient numeric columns "
                "for correlation analysis."
            )

        strongest_pair = max(
            correlations,
            key=lambda x: abs(
                correlations[x]
            )
        )

        value = correlations[
            strongest_pair
        ]

        insight = (
            f"The strongest detected "
            f"relationship is between "
            f"{strongest_pair} "
            f"with a correlation of "
            f"{value:.3f}."
        )

        # Add business context
        abs_value = abs(value)
        if abs_value > 0.8:
            insight += " Very strong correlation suggests these metrics move together closely - changes in one likely predict changes in the other."
        elif abs_value > 0.6:
            insight += " Strong correlation indicates a meaningful relationship worth investigating for potential causal links or common drivers."
        elif abs_value > 0.3:
            insight += " Moderate correlation suggests some association exists, though other factors likely influence the relationship."
        else:
            insight += " Weak correlation indicates little linear relationship between these metrics."

        if value > 0:
            insight += " Positive relationship means as one increases, the other tends to increase."
        else:
            insight += " Negative relationship means as one increases, the other tends to decrease."

        return insight

    def generate_outlier_insight(self):

        outlier_report = self.eda_report.get(
            "outlier_analysis",
            {}
        )

        if not outlier_report:

            return (
                "No outlier analysis was available."
            )

        highest_column = max(
            outlier_report,
            key=lambda x:
            outlier_report[x][
                "outlier_count"
            ]
        )

        count = outlier_report[
            highest_column
        ][
            "outlier_count"
        ]

        percentage = outlier_report[
            highest_column
        ][
            "outlier_percentage"
        ]

        insight = (
            f"{highest_column} contains "
            f"{count:,} potential outliers "
            f"representing {percentage}% "
            f"of the records."
        )

        # Add business context
        if percentage > 10:
            insight += " High outlier concentration suggests potential data quality issues, measurement errors, or significant business events requiring investigation."
        elif percentage > 5:
            insight += " Moderate outlier presence warrants review to determine if outliers represent valuable insights or data quality concerns."
        elif percentage > 1:
            insight += " Low outlier rate is typical for most datasets; investigate individual outliers for potential business significance."
        else:
            insight += " Very few outliers detected indicates consistent data patterns."

        return insight

    def generate_data_quality_insight(self):

        missing_values = self.eda_report.get(
            "missing_value_analysis",
            {}
        )

        if not missing_values:

            return (
                "No missing values were detected."
            )

        column = max(
            missing_values,
            key=missing_values.get
        )

        count = missing_values[column]
        total_rows = self.eda_report.get("dataset_summary", {}).get("rows", 1)
        missing_pct = (count / total_rows) * 100 if total_rows > 0 else 0

        insight = (
            f"The column '{column}' contains "
            f"the highest number of missing "
            f"values ({count:,}, {missing_pct:.1f}% of total)."
        )

        # Add business context
        if missing_pct > 50:
            insight += " Severe missing data in this column severely limits its usability for analysis and may require alternative data sources or collection methods."
        elif missing_pct > 20:
            insight += " High missing data rate requires careful consideration - analysis results may be biased and imputation methods should be evaluated."
        elif missing_pct > 10:
            insight += " Moderate missing data should be addressed through imputation or careful interpretation of results."
        elif missing_pct > 5:
            insight += " Low missing data level is acceptable for most analyses with minimal impact on results."
        else:
            insight += " Very low missing data indicates good data collection practices for this field."

        return insight

    def generate_all_insights(self):

        return [

            self.generate_dataset_summary_insight(),

            self.generate_numeric_insight(),

            self.generate_categorical_insight(),

            self.generate_date_insight(),

            self.generate_correlation_insight(),

            self.generate_outlier_insight(),

            self.generate_data_quality_insight()

        ]