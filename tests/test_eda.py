import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.ingestion.data_loader import DataLoader
from src.eda.exploratory_analysis import ExploratoryAnalysis


def test_eda():
    df = DataLoader.load_data("data/raw/sales_data.csv")

    eda = ExploratoryAnalysis(df)

    report = eda.generate_eda_report()

    # Check that the report is a dict and has expected sections
    assert isinstance(report, dict)
    assert "dataset_summary" in report
    assert "numeric_summary" in report
    assert "categorical_summary" in report
    # Check that the dataset summary has rows and columns
    assert report["dataset_summary"]["rows"] > 0
    assert report["dataset_summary"]["columns"] > 0