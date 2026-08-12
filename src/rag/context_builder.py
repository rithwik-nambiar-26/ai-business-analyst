class ContextBuilder:

    def __init__(self, eda_report, insights):

        self.eda_report = eda_report
        self.insights = insights

    def build_context(self):
        # Build a generic context from the eda_report and insights
        context_parts = []

        # Dataset overview
        dataset_summary = self.eda_report.get("dataset_summary", {})
        if dataset_summary:
            context_parts.append("DATASET OVERVIEW")
            context_parts.append(f"Rows: {dataset_summary.get('rows', 'N/A')}")
            context_parts.append(f"Columns: {dataset_summary.get('columns', 'N/A')}")
            context_parts.append(f"Missing Values: {dataset_summary.get('missing_values', 'N/A')}")
            context_parts.append(f"Duplicate Rows: {dataset_summary.get('duplicate_rows', 'N/A')}")
            context_parts.append("")  # blank line

        # Numeric summary
        numeric_summary = self.eda_report.get("numeric_summary", {})
        if numeric_summary:
            context_parts.append("NUMERIC SUMMARY")
            # Limit to first 5 numeric columns to avoid too long context
            for col, stats in list(numeric_summary.items())[:5]:
                context_parts.append(f"Column: {col}")
                for stat_name, stat_val in stats.items():
                    context_parts.append(f"  {stat_name}: {stat_val}")
                context_parts.append("")  # blank line after each column

        # Categorical summary
        categorical_summary = self.eda_report.get("categorical_summary", {})
        if categorical_summary:
            context_parts.append("CATEGORICAL SUMMARY")
            # Limit to first 5 categorical columns
            for col, values in list(categorical_summary.items())[:5]:
                context_parts.append(f"Column: {col}")
                # Show top 3 category values
                for val, count in list(values.items())[:3]:
                    context_parts.append(f"  {val}: {count}")
                context_parts.append("")

        # Date summary
        date_summary = self.eda_report.get("date_summary", {})
        if date_summary:
            context_parts.append("DATE SUMMARY")
            for col, details in date_summary.items():
                context_parts.append(f"Column: {col}")
                for detail_name, detail_val in details.items():
                    context_parts.append(f"  {detail_name}: {detail_val}")
                context_parts.append("")

        # Correlation analysis
        correlation_analysis = self.eda_report.get("correlation_analysis", {})
        if correlation_analysis:
            context_parts.append("CORRELATION ANALYSIS")
            # Show top 5 correlations by absolute value
            sorted_corr = sorted(correlation_analysis.items(), key=lambda x: abs(x[1]), reverse=True)
            for pair, value in sorted_corr[:5]:
                context_parts.append(f"  {pair}: {value}")
            context_parts.append("")

        # Missing value analysis
        missing_value_analysis = self.eda_report.get("missing_value_analysis", {})
        if missing_value_analysis:
            context_parts.append("MISSING VALUE ANALYSIS")
            # Show columns with missing values
            for col, count in missing_value_analysis.items():
                if count > 0:
                    context_parts.append(f"  {col}: {count}")
            context_parts.append("")

        # Outlier analysis
        outlier_analysis = self.eda_report.get("outlier_analysis", {})
        if outlier_analysis:
            context_parts.append("OUTLIER ANALYSIS")
            # Show columns with outliers
            for col, details in outlier_analysis.items():
                if details['outlier_count'] > 0:
                    context_parts.append(f"  {col}: {details['outlier_count']} outliers ({details['outlier_percentage']}%)")
            context_parts.append("")

        # Insights - now expecting BusinessInsight objects or dicts
        if self.insights:
            context_parts.append("BUSINESS INSIGHTS")
            for i, insight in enumerate(self.insights, start=1):
                # Handle both BusinessInsight objects and dictionaries
                if hasattr(insight, 'insight'):
                    insight_text = insight.insight
                elif isinstance(insight, dict) and 'insight' in insight:
                    insight_text = insight['insight']
                else:
                    insight_text = str(insight)
                context_parts.append(f"  Insight {i}: {insight_text}")

        return "\n".join(context_parts)