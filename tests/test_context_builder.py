import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ingestion.data_loader import DataLoader
from src.eda.exploratory_analysis import ExploratoryAnalysis
from src.insights.insight_generator import InsightGenerator
from src.rag.context_builder import ContextBuilder


def test_context_builder():
    df = DataLoader.load_data("data/raw/sales_data.csv")

    eda = ExploratoryAnalysis(df)

    eda_report = eda.generate_eda_report()

    insights = InsightGenerator(
        eda_report
    ).generate_all_insights()

    context = ContextBuilder(
        eda_report,
        insights
    ).build_context()

    # Check that context is a string and contains expected sections
    assert isinstance(context, str)
    assert "DATASET OVERVIEW" in context
    assert "NUMERIC SUMMARY" in context
    # Check that at least one insight is included
    assert "Insight 1:" in context or "BUSINESS INSIGHTS" in context