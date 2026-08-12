"""
Business Insight Engine for generating analyst-style insights from EDA reports.
This module transforms statistical findings into actionable business insights.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class BusinessInsight:
    """Represents a business insight with supporting evidence."""
    insight: str
    category: str  # e.g., 'performance', 'risk', 'opportunity', 'trend'
    confidence: str  # e.g., 'high', 'medium', 'low'
    supporting_data: Dict[str, Any]
    suggested_action: Optional[str] = None


class BusinessInsightEngine:
    """
    Generates business insights from exploratory data analysis reports.
    Focuses on creating analyst-style interpretations rather than just statistics.
    """

    def __init__(self, eda_report: Dict[str, Any]):
        self.eda_report = eda_report
        self.insights = []

    def generate_all_insights(self) -> List[BusinessInsight]:
        """Generate all types of business insights."""
        self.insights = []

        # Generate insights in order of priority
        self._generate_performance_insights()
        self._generate_risk_insights()
        self._generate_opportunity_insights()
        self._generate_trend_insights()
        self._generate_data_quality_insights()

        return self.insights

    def _generate_performance_insights(self):
        """Generate insights about business performance."""
        numeric_summary = self.eda_report.get("numeric_summary", {})
        categorical_summary = self.eda_report.get("categorical_summary", {})
        correlations = self.eda_report.get("correlation_analysis", {})

        # Insight 1: Identify top performing metrics
        if numeric_summary:
            # Find metrics with highest values or best performance indicators
            for col, stats in numeric_summary.items():
                if 'mean' in stats and 'std' in stats:
                    # Simple performance scoring: high mean relative to std suggests consistent performance
                    if stats['std'] > 0:
                        performance_score = stats['mean'] / stats['std']
                        if performance_score > 2:  # Arbitrary threshold for good performance
                            self.insights.append(BusinessInsight(
                                insight=f"The '{col}' metric shows strong performance with an average value of {stats['mean']:,.2f} and consistent delivery (low volatility).",
                                category="performance",
                                confidence="medium",
                                supporting_data={"metric": col, "mean": stats['mean'], "std": stats['std']},
                                suggested_action=f"Monitor {col} closely as it's a key strength area."
                            ))

        # Insight 2: Top categorical performers
        if categorical_summary:
            for col, values in categorical_summary.items():
                if values:
                    top_value = max(values, key=values.get)
                    top_count = values[top_value]
                    total = sum(values.values())
                    percentage = (top_count / total) * 100 if total > 0 else 0

                    if percentage > 40:  # Dominant category
                        self.insights.append(BusinessInsight(
                            insight=f"The '{col}' field is dominated by '{top_value}' ({percentage:.1f}% of records), suggesting strong market concentration.",
                            category="performance",
                            confidence="high",
                            supporting_data={"field": col, "top_value": top_value, "percentage": percentage},
                            suggested_action=f"Consider diversification strategies for {col} to reduce dependency on '{top_value}'."
                        ))

    def _generate_risk_insights(self):
        """Generate insights about potential risks and concerns."""
        outliers = self.eda_report.get("outlier_analysis", {})
        missing_values = self.eda_report.get("missing_value_analysis", {})
        numeric_summary = self.eda_report.get("numeric_summary", {})

        # Insight 1: High outlier percentages indicate data quality or operational risks
        for col, details in outliers.items():
            if details['outlier_percentage'] > 15:  # High outlier percentage
                self.insights.append(BusinessInsight(
                    insight=f"The '{col}' metric shows {details['outlier_percentage']:.1f}% outliers, indicating potential data quality issues or unusual business events requiring investigation.",
                    category="risk",
                    confidence="high",
                    supporting_data={"column": col, "outlier_count": details['outlier_count'], "percentage": details['outlier_percentage']},
                    suggested_action=f"Investigate the root cause of outliers in {col} - could indicate data entry errors, fraud, or exceptional business events."
                ))

        # Insight 2: Significant missing values in key metrics
        for col, count in missing_values.items():
            total_rows = self.eda_report.get("dataset_summary", {}).get("rows", 1)
            missing_pct = (count / total_rows) * 100 if total_rows > 0 else 0

            if missing_pct > 10 and col in numeric_summary:  # Important metric with missing data
                self.insights.append(BusinessInsight(
                    insight=f"Critical data gap: {missing_pct:.1f}% of '{col}' values are missing, which may significantly impact analysis accuracy and decision-making.",
                    category="risk",
                    confidence="high",
                    supporting_data={"column": col, "missing_count": count, "missing_percentage": missing_pct},
                    suggested_action=f"Implement data collection improvements for {col} to reduce missing values below 5%."
                ))

    def _generate_opportunity_insights(self):
        """Generate insights about business opportunities."""
        numeric_summary = self.eda_report.get("numeric_summary", {})
        correlations = self.eda_report.get("correlation_analysis", {})
        categorical_summary = self.eda_report.get("categorical_summary", {})

        # Insight 1: Strong positive correlations suggest leverage points
        strong_pos_correlations = []
        for pair, corr in correlations.items():
            if corr > 0.7:  # Strong positive correlation
                strong_pos_correlations.append((pair, corr))

        if strong_pos_correlations:
            # Take the strongest correlation
            strongest_pair, strongest_corr = max(strong_pos_correlations, key=lambda x: x[1])
            self.insights.append(BusinessInsight(
                insight=f"Strong positive relationship ({strongest_corr:.3f}) detected between {strongest_pair}. Improving one metric likely improves the other.",
                category="opportunity",
                confidence="medium",
                supporting_data={"metric_pair": strongest_pair, "correlation": strongest_corr},
                suggested_action=f"Focus on improving {strongest_pair.split(' vs ')[0]} as it strongly correlates with {strongest_pair.split(' vs ')[1]}."
            ))

        # Insight 2: Underperforming segments with high potential
        if numeric_summary and categorical_summary:
            for cat_col, cat_values in categorical_summary.items():
                if len(cat_values) > 1:
                    # Find categories with below-average performance in key metrics
                    for num_col, num_stats in numeric_summary.items():
                        if 'mean' in num_stats:
                            overall_avg = num_stats['mean']
                            # This is simplified - in reality we'd need to group by category
                            # For now, we'll note the opportunity for segmentation analysis
                            if len(cat_values) >= 3:  # Enough segments to analyze
                                self.insights.append(BusinessInsight(
                                    insight=f"The '{cat_col}' field has {len(cat_values)} distinct segments, suggesting opportunities for targeted strategies based on segment performance.",
                                    category="opportunity",
                                    confidence="low",
                                    supporting_data={"segment_field": cat_col, "segment_count": len(cat_values)},
                                    suggested_action=f"Analyze performance of {num_col} across different {cat_col} segments to identify high/low performers."
                                ))
                                break  # Just one insight per categorical field for now
                    break  # Just one opportunity insight for now

    def _generate_trend_insights(self):
        """Generate insights about trends and changes over time."""
        date_summary = self.eda_report.get("date_summary", {})
        numeric_summary = self.eda_report.get("numeric_summary", {})

        # Insight 1: Time-series data available for trend analysis
        if date_summary and numeric_summary:
            date_col = list(date_summary.keys())[0] if date_summary else None
            if date_col:
                date_info = date_summary[date_col]
                self.insights.append(BusinessInsight(
                    insight=f"Dataset spans {date_info.get('start_date', 'unknown')} to {date_info.get('end_date', 'unknown')} ({date_info.get('records', 0)} time-period records), enabling trend analysis and forecasting.",
                    category="trend",
                    confidence="high",
                    supporting_data={"date_column": date_col, "start_date": date_info.get('start_date'), "end_date": date_info.get('end_date')},
                    suggested_action="Use forecasting capabilities to predict future trends and plan accordingly."
                ))

    def _generate_data_quality_insights(self):
        """Generate insights about data quality issues."""
        dataset_summary = self.eda_report.get("dataset_summary", {})
        missing_values = self.eda_report.get("missing_value_analysis", {})
        duplicate_rows = self.eda_report.get("dataset_summary", {}).get("duplicate_rows", 0)

        # Overall data quality assessment
        total_rows = dataset_summary.get("rows", 1)
        total_missing = sum(missing_values.values()) if missing_values else 0

        if total_rows > 0:
            missing_pct = (total_missing / (total_rows * len(self.eda_report.get("column_names", [])))) * 100 if self.eda_report.get("column_names") else 0
            duplicate_pct = (duplicate_rows / total_rows) * 100 if total_rows > 0 else 0

            if missing_pct > 5 or duplicate_pct > 5:
                quality_issues = []
                if missing_pct > 5:
                    quality_issues.append(f"{missing_pct:.1f}% missing data")
                if duplicate_pct > 5:
                    quality_issues.append(f"{duplicate_pct:.1f}% duplicate records")

                self.insights.append(BusinessInsight(
                    insight=f"Data quality concerns detected: {', '.join(quality_issues)}. This may affect the reliability of analytical results.",
                    category="risk",
                    confidence="medium",
                    supporting_data={"missing_percentage": missing_pct, "duplicate_percentage": duplicate_pct},
                    suggested_action="Invest in data cleaning and validation processes to improve data quality before critical decision-making."
                ))

    def get_insights_summary(self) -> List[Dict[str, Any]]:
        """Get insights in a format suitable for display or API response."""
        return [
            {
                "insight": insight.insight,
                "category": insight.category,
                "confidence": insight.confidence,
                "supporting_data": insight.supporting_data,
                "suggested_action": insight.suggested_action
            }
            for insight in self.insights
        ]