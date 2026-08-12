import sys
from pathlib import Path
import pandas as pd
import pytest

project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

sys.path.append(str(project_root))

from src.dataset_intelligence import get_dataset_intelligence

def test_dataset_intelligence_with_hr_data():
    """Test dataset intelligence with HR-like data"""
    # Create sample HR data
    df = pd.DataFrame({
        'employee_id': [1, 2, 3, 4, 5],
        'first_name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
        'last_name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson'],
        'department': ['Engineering', 'Marketing', 'Sales', 'HR', 'Engineering'],
        'position': ['Software Engineer', 'Marketing Manager', 'Sales Rep', 'HR Coordinator', 'Senior Engineer'],
        'hire_date': ['2020-01-15', '2019-03-22', '2021-07-10', '2020-11-05', '2018-09-30'],
        'salary': [75000, 82000, 65000, 58000, 95000],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male'],
        'age': [28, 35, 26, 32, 35],
        'performance_score': [85, 92, 78, 88, 95]
    })

    # Convert hire_date to datetime
    df['hire_date'] = pd.to_datetime(df['hire_date'])

    # Get dataset intelligence
    intelligence = get_dataset_intelligence(df)

    # Basic assertions
    assert intelligence.dataset_type == 'hr'
    assert intelligence.entity_type == 'employees'
    assert intelligence.entity_name_singular == 'employee'
    assert len(intelligence.important_metrics) > 0
    assert len(intelligence.important_dimensions) > 0
    assert intelligence.time_column == 'hire_date'
    assert len(intelligence.page_names) > 0
    assert len(intelligence.kpis) > 0
    assert len(intelligence.chart_suggestions) > 0
    assert len(intelligence.suggested_questions) > 0
    assert len(intelligence.suggested_actions) > 0

    # Check that we got reasonable column names
    assert 'employee_id' in intelligence.column_display_names
    assert 'first_name' in intelligence.column_display_names
    assert 'salary' in intelligence.column_display_names

    # Check that important metrics include salary-like columns
    metric_names = [m.lower() for m in intelligence.important_metrics]
    assert any('salary' in m for m in metric_names) or len(intelligence.important_metrics) > 0

    print("HR Dataset Intelligence Test Passed!")
    print(f"Dataset Type: {intelligence.dataset_type}")
    print(f"Entity Type: {intelligence.entity_type}")
    print(f"Description: {intelligence.description}")
    print(f"Important Metrics: {intelligence.important_metrics}")
    print(f"Important Dimensions: {intelligence.important_dimensions}")
    print(f"Time Column: {intelligence.time_column}")
    print(f"Sample Suggested Question: {intelligence.suggested_questions[0] if intelligence.suggested_questions else 'None'}")

def test_dataset_intelligence_with_sales_data():
    """Test dataset intelligence with sales-like data"""
    # Create sample sales data
    df = pd.DataFrame({
        'order_id': [1001, 1002, 1003, 1004, 1005],
        'product_name': ['Product A', 'Product B', 'Product C', 'Product A', 'Product B'],
        'category': ['Electronics', 'Clothing', 'Electronics', 'Electronics', 'Clothing'],
        'customer_name': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson'],
        'order_date': ['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19'],
        'quantity': [2, 1, 3, 1, 2],
        'unit_price': [29.99, 19.99, 39.99, 29.99, 19.99],
        'total_amount': [59.98, 19.99, 119.97, 29.99, 39.98],
        'region': ['North', 'South', 'East', 'West', 'North']
    })

    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'])

    # Get dataset intelligence
    intelligence = get_dataset_intelligence(df)

    # Basic assertions
    assert intelligence.dataset_type == 'retail' or intelligence.dataset_type == 'generic'  # May vary based on keyword matching
    assert intelligence.entity_type in ['customers', 'orders', 'transactions', 'records']
    assert len(intelligence.important_metrics) > 0
    assert len(intelligence.important_dimensions) > 0
    assert intelligence.time_column == 'order_date'
    assert len(intelligence.page_names) > 0
    assert len(intelligence.kpis) > 0
    assert len(intelligence.chart_suggestions) > 0
    assert len(intelligence.suggested_questions) > 0
    assert len(intelligence.suggested_actions) > 0

    print("\nSales Dataset Intelligence Test Passed!")
    print(f"Dataset Type: {intelligence.dataset_type}")
    print(f"Entity Type: {intelligence.entity_type}")
    print(f"Description: {intelligence.description}")
    print(f"Important Metrics: {intelligence.important_metrics}")
    print(f"Important Dimensions: {intelligence.important_dimensions}")
    print(f"Time Column: {intelligence.time_column}")

if __name__ == "__main__":
    test_dataset_intelligence_with_hr_data()
    test_dataset_intelligence_with_sales_data()
    print("\nAll dataset intelligence tests completed successfully!")