import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ingestion.data_loader import DataLoader
from src.eda.exploratory_analysis import ExploratoryAnalysis
from src.insights.insight_generator import InsightGenerator


def test_insights():
    df = DataLoader.load_data("data/raw/sales_data.csv")

    eda = ExploratoryAnalysis(df)

    eda_report = eda.generate_eda_report()

    insight_generator = InsightGenerator(
        eda_report
    )

    insights = insight_generator.generate_all_insights()

    # Check that we get a list of strings
    assert isinstance(insights, list)
    assert all(isinstance(insight, str) for insight in insights)
    # Check that we have at least one insight
    assert len(insights) > 0
    # Check that each insight is non-empty
    for insight in insights:
        assert insight.strip() != ""