import pytest
import pandas as pd
import numpy as np
from src.profiling.data_profiler import DataProfiler

def test_profile_dataset():
    # Construct synthetic data
    df = pd.DataFrame({
        "dates": pd.date_range(start="2026-01-01", periods=10),
        "values": [1.5, 2.5, 3.5, np.nan, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5],
        "label": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"]
    })

    profiler = DataProfiler(df)
    profile = profiler.generate_profile()
    assert profile["rows"] == 10
    assert profile["columns"] == 3
    assert profile["missing_values"]["values"] == 1
    assert "values" in profile["column_names"]
    assert "dates" in profile["data_types"]
    assert "label" in profile["data_types"]
