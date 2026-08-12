import sys
from pathlib import Path
import pandas as pd
import tempfile
import os

project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

sys.path.append(str(project_root))

from app.utils.data_manager import DataManager
from src.dataset_intelligence import get_dataset_intelligence
from src.insights.business_insight_engine import BusinessInsightEngine
from src.eda.exploratory_analysis import ExploratoryAnalysis

def test_hr_dataset_driven_behavior():
    """Test that the application adapts correctly to HR data"""
    print("Testing HR Dataset Driven Behavior...")

    # Create HR dataset
    hr_data = pd.DataFrame({
        'employee_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
        'first_name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Davis', 'Evelyn', 'Frank'],
        'last_name': ['Doe', 'Smith', 'Johnson', 'Brown', 'Wilson', 'Lee', 'Clark', 'Taylor'],
        'department': ['Engineering', 'Marketing', 'Sales', 'HR', 'Engineering', 'Marketing', 'Sales', 'Engineering'],
        'position': ['Software Engineer', 'Marketing Manager', 'Sales Rep', 'HR Coordinator', 'Senior Engineer',
                    'Marketing Analyst', 'Sales Manager', 'DevOps Engineer'],
        'hire_date': ['2020-01-15', '2019-03-22', '2021-07-10', '2020-11-05', '2018-09-30',
                     '2021-02-14', '2019-12-03', '2020-06-18'],
        'salary': [75000, 82000, 65000, 58000, 95000, 68000, 88000, 82000],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Female', 'Male'],
        'age': [28, 35, 26, 32, 35, 29, 34, 31],
        'performance_score': [85, 92, 78, 88, 95, 81, 89, 87]
    })

    # Convert dates
    hr_data['hire_date'] = pd.to_datetime(hr_data['hire_date'])

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        hr_data.to_csv(f.name, index=False)
        hr_file_path = f.name

    try:
        # Load dataset through DataManager (simulating upload)
        from src.ingestion.data_loader import DataLoader
        df = DataLoader.load_data(hr_file_path)
        DataManager.store_dataset(df)

        # Get dataset intelligence
        intelligence = DataManager.get_dataset_intelligence()

        print("Dataset Type Detected:", intelligence.get('dataset_type'))
        print("Entity Type:", intelligence.get('entity_type'))
        print("Description:", intelligence.get('description')[:100] + "...")

        # Verify HR-specific adaptations
        assert intelligence.get('dataset_type') == 'hr', f"Expected 'hr', got {intelligence.get('dataset_type')}"
        assert intelligence.get('entity_type') == 'employees', f"Expected 'employees', got {intelligence.get('entity_type')}"
        assert 'human resources' in intelligence.get('description').lower() or 'employee' in intelligence.get('description').lower()

        # Check that important metrics are HR-relevant
        important_metrics = intelligence.get('important_metrics', [])
        print("Important Metrics:", important_metrics)
        hr_relevant_metrics = ['salary', 'age', 'performance_score']
        assert any(metric in str(important_metrics).lower() for metric in hr_relevant_metrics), \
            f"No HR-relevant metrics found in {important_metrics}"

        # Check that important dimensions are HR-relevant
        important_dimensions = intelligence.get('important_dimensions', [])
        print("Important Dimensions:", important_dimensions)
        hr_relevant_dimensions = ['department', 'gender', 'position']
        assert any(dim in str(important_dimensions).lower() for dim in hr_relevant_dimensions), \
            f"No HR-relevant dimensions found in {important_dimensions}"

        # Check time column
        time_column = intelligence.get('time_column')
        print("Time Column:", time_column)
        assert time_column == 'hire_date', f"Expected 'hire_date', got {time_column}"

        # Check suggested questions are HR-relevant
        suggested_questions = intelligence.get('suggested_questions', [])
        print("Sample Suggested Question:", suggested_questions[0] if suggested_questions else 'None')
        hr_question_indicators = ['employee', 'department', 'salary', 'performance', 'hire', 'workforce']
        assert any(indicator in str(suggested_questions).lower() for indicator in hr_question_indicators), \
            f"No HR-relevant questions found in {suggested_questions}"

        # Check page names are HR-relevant
        page_names = intelligence.get('page_names', [])
        print("Page Names:", page_names)
        hr_page_indicators = ['employee', 'department', 'compensation', 'workforce', 'performance']
        assert any(indicator in str(page_names).lower() for indicator in hr_page_indicators), \
            f"No HR-relevant page names found in {page_names}"

        # Test that insights are generated appropriately
        eda = ExploratoryAnalysis(df)
        eda_report = eda.generate_eda_report()

        business_insight_engine = BusinessInsightEngine(eda_report)
        business_insights = business_insight_engine.generate_all_insights()

        print("Number of Business Insights Generated:", len(business_insights))
        assert len(business_insights) > 0, "No business insights generated for HR data"

        # Check that insights contain HR-relevant content
        insight_texts = [insight.insight for insight in business_insights]
        combined_insights = ' '.join(insight_texts).lower()
        hr_insight_indicators = ['employee', 'salary', 'department', 'performance', 'hire', 'workforce']
        assert any(indicator in combined_insights for indicator in hr_insight_indicators), \
            f"No HR-relevant content found in insights: {combined_insights[:200]}..."

        print("HR Dataset Driven Behavior Test PASSED\n")
        return True

    finally:
        # Clean up temp file
        if os.path.exists(hr_file_path):
            os.unlink(hr_file_path)

def test_retail_dataset_driven_behavior():
    """Test that the application adapts correctly to retail/sales data"""
    print("Testing Retail Dataset Driven Behavior...")

    # Create retail dataset
    retail_data = pd.DataFrame({
        'order_id': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
        'product_name': ['Laptop', 'T-Shirt', 'Phone', 'Laptop', 'Jeans', 'Headphones', 'Shoes', 'Monitor'],
        'category': ['Electronics', 'Clothing', 'Electronics', 'Electronics', 'Clothing', 'Electronics', 'Clothing', 'Electronics'],
        'customer_name': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Wilson', 'Davis Lee', 'Evelyn Clark', 'Frank Taylor'],
        'order_date': ['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20', '2023-01-21', '2023-01-22'],
        'quantity': [1, 2, 1, 1, 3, 1, 2, 1],
        'unit_price': [999.99, 19.99, 699.99, 999.99, 49.99, 149.99, 79.99, 299.99],
        'total_amount': [999.99, 39.98, 699.99, 999.99, 149.97, 149.99, 159.98, 299.99],
        'region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
        'payment_method': ['Credit Card', 'PayPal', 'Credit Card', 'Debit Card', 'Credit Card', 'PayPal', 'Credit Card', 'Debit Card']
    })

    # Convert dates
    retail_data['order_date'] = pd.to_datetime(retail_data['order_date'])

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        retail_data.to_csv(f.name, index=False)
        retail_file_path = f.name

    try:
        # Load dataset through DataManager (simulating upload)
        from src.ingestion.data_loader import DataLoader
        df = DataLoader.load_data(retail_file_path)
        DataManager.store_dataset(df)

        # Get dataset intelligence
        intelligence = DataManager.get_dataset_intelligence()

        print("Dataset Type Detected:", intelligence.get('dataset_type'))
        print("Entity Type:", intelligence.get('entity_type'))
        print("Description:", intelligence.get('description')[:100] + "...")

        # Verify retail-specific adaptations (may be classified as retail or generic)
        dataset_type = intelligence.get('dataset_type')
        assert dataset_type in ['retail', 'generic'], f"Expected 'retail' or 'generic', got {dataset_type}"

        if dataset_type == 'retail':
            assert intelligence.get('entity_type') in ['customers', 'transactions', 'orders'], \
                f"Expected retail entity type, got {intelligence.get('entity_type')}"
            assert 'retail' in intelligence.get('description').lower() or 'sales' in intelligence.get('description').lower() or 'transaction' in intelligence.get('description').lower()

        # Check that important metrics are retail-relevant
        important_metrics = intelligence.get('important_metrics', [])
        print("Important Metrics:", important_metrics)
        retail_relevant_metrics = ['quantity', 'unit_price', 'total_amount', 'price', 'amount', 'sales', 'revenue']
        assert any(metric in str(important_metrics).lower() for metric in retail_relevant_metrics), \
            f"No retail-relevant metrics found in {important_metrics}"

        # Check that important dimensions are retail-relevant
        important_dimensions = intelligence.get('important_dimensions', [])
        print("Important Dimensions:", important_dimensions)
        retail_relevant_dimensions = ['product_name', 'category', 'region', 'customer_name', 'payment_method']
        assert any(dim in str(important_dimensions).lower() for dim in retail_relevant_dimensions), \
            f"No retail-relevant dimensions found in {important_dimensions}"

        # Check time column
        time_column = intelligence.get('time_column')
        print("Time Column:", time_column)
        assert time_column == 'order_date', f"Expected 'order_date', got {time_column}"

        # Check suggested questions are retail-relevant
        suggested_questions = intelligence.get('suggested_questions', [])
        print("Sample Suggested Question:", suggested_questions[0] if suggested_questions else 'None')
        retail_question_indicators = ['product', 'sales', 'customer', 'revenue', 'order', 'region', 'category', 'price']
        assert any(indicator in str(suggested_questions).lower() for indicator in retail_question_indicators), \
            f"No retail-relevant questions found in {suggested_questions}"

        # Check page names are retail-relevant
        page_names = intelligence.get('page_names', [])
        print("Page Names:", page_names)
        retail_page_indicators = ['sales', 'product', 'customer', 'order', 'revenue', 'store', 'category']
        assert any(indicator in str(page_names).lower() for indicator in retail_page_indicators), \
            f"No retail-relevant page names found in {page_names}"

        # Test that insights are generated appropriately
        eda = ExploratoryAnalysis(df)
        eda_report = eda.generate_eda_report()

        business_insight_engine = BusinessInsightEngine(eda_report)
        business_insights = business_insight_engine.generate_all_insights()

        print("Number of Business Insights Generated:", len(business_insights))
        assert len(business_insights) > 0, "No business insights generated for retail data"

        # Check that insights contain retail-relevant content
        insight_texts = [insight.insight for insight in business_insights]
        combined_insights = ' '.join(insight_texts).lower()
        retail_insight_indicators = ['product', 'sales', 'customer', 'revenue', 'order', 'price', 'quantity', 'region']
        assert any(indicator in combined_insights for indicator in retail_insight_indicators), \
            f"No retail-relevant content found in insights: {combined_insights[:200]}..."

        print("Retail Dataset Driven Behavior Test PASSED\n")
        return True

    finally:
        # Clean up temp file
        if os.path.exists(retail_file_path):
            os.unlink(retail_file_path)

def test_financial_dataset_driven_behavior():
    """Test that the application adapts correctly to financial data"""
    print("Testing Financial Dataset Driven Behavior...")

    # Create financial dataset
    financial_data = pd.DataFrame({
        'transaction_id': ['TX001', 'TX002', 'TX003', 'TX004', 'TX005', 'TX006', 'TX007', 'TX008'],
        'date': ['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20', '2023-01-21', '2023-01-22'],
        'description': ['Salary Deposit', 'Grocery Store', 'Gas Station', 'Online Shopping', 'Transfer to Savings', 'Restaurant', 'Electric Bill', 'Movie Theater'],
        'category': ['Income', 'Expense', 'Expense', 'Expense', 'Transfer', 'Expense', 'Expense', 'Expense'],
        'amount': [2500.00, -85.50, -60.00, -120.00, -500.00, -45.00, -120.00, -25.00],
        'balance': [2500.00, 2414.50, 2354.50, 2234.50, 1734.50, 1689.50, 1569.50, 1544.50],
        'account_type': ['Checking', 'Checking', 'Checking', 'Checking', 'Savings', 'Checking', 'Checking', 'Checking'],
        'payment_method': ['Deposit', 'Debit Card', 'Debit Card', 'Credit Card', 'Transfer', 'Debit Card', 'Bank Transfer', 'Debit Card']
    })

    # Convert dates
    financial_data['date'] = pd.to_datetime(financial_data['date'])

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        financial_data.to_csv(f.name, index=False)
        financial_file_path = f.name

    try:
        # Load dataset through DataManager (simulating upload)
        from src.ingestion.data_loader import DataLoader
        df = DataLoader.load_data(financial_file_path)
        DataManager.store_dataset(df)

        # Get dataset intelligence
        intelligence = DataManager.get_dataset_intelligence()

        print("Dataset Type Detected:", intelligence.get('dataset_type'))
        print("Entity Type:", intelligence.get('entity_type'))
        print("Description:", intelligence.get('description')[:100] + "...")

        # Verify financial-specific adaptations (may be classified as finance or generic)
        dataset_type = intelligence.get('dataset_type')
        assert dataset_type in ['finance', 'generic'], f"Expected 'finance' or 'generic', got {dataset_type}"

        if dataset_type == 'finance':
            assert intelligence.get('entity_type') in ['transactions', 'records'], \
                f"Expected financial entity type, got {intelligence.get('entity_type')}"
            assert 'financial' in intelligence.get('description').lower() or 'transaction' in intelligence.get('description').lower() or 'expense' in intelligence.get('description').lower()

        # Check that important metrics are financial-relevant
        important_metrics = intelligence.get('important_metrics', [])
        print("Important Metrics:", important_metrics)
        financial_relevant_metrics = ['amount', 'balance', 'income', 'expense']
        assert any(metric in str(important_metrics).lower() for metric in financial_relevant_metrics), \
            f"No financial-relevant metrics found in {important_metrics}"

        # Check that important dimensions are financial-relevant
        important_dimensions = intelligence.get('important_dimensions', [])
        print("Important Dimensions:", important_dimensions)
        financial_relevant_dimensions = ['category', 'account_type', 'payment_method', 'description']
        assert any(dim in str(important_dimensions).lower() for dim in financial_relevant_dimensions), \
            f"No financial-relevant dimensions found in {important_dimensions}"

        # Check time column
        time_column = intelligence.get('time_column')
        print("Time Column:", time_column)
        assert time_column == 'date', f"Expected 'date', got {time_column}"

        # Check suggested questions are financial-relevant
        suggested_questions = intelligence.get('suggested_questions', [])
        print("Sample Suggested Question:", suggested_questions[0] if suggested_questions else 'None')
        financial_question_indicators = ['transaction', 'expense', 'income', 'balance', 'spending', 'money', 'account']
        assert any(indicator in str(suggested_questions).lower() for indicator in financial_question_indicators), \
            f"No financial-relevant questions found in {suggested_questions}"

        # Check page names are financial-relevant
        page_names = intelligence.get('page_names', [])
        print("Page Names:", page_names)
        financial_page_indicators = ['transaction', 'income', 'expense', 'balance', 'account', 'financial', 'money']
        assert any(indicator in str(page_names).lower() for indicator in financial_page_indicators), \
            f"No financial-relevant page names found in {page_names}"

        # Test that insights are generated appropriately
        eda = ExploratoryAnalysis(df)
        eda_report = eda.generate_eda_report()

        business_insight_engine = BusinessInsightEngine(eda_report)
        business_insights = business_insight_engine.generate_all_insights()

        print("Number of Business Insights Generated:", len(business_insights))
        assert len(business_insights) > 0, "No business insights generated for financial data"

        # Check that insights contain financial-relevant content
        insight_texts = [insight.insight for insight in business_insights]
        combined_insights = ' '.join(insight_texts).lower()
        financial_insight_indicators = ['transaction', 'amount', 'expense', 'income', 'balance', 'money', 'account', 'spending']
        assert any(indicator in combined_insights for indicator in financial_insight_indicators), \
            f"No financial-relevant content found in insights: {combined_insights[:200]}..."

        print("Financial Dataset Driven Behavior Test PASSED\n")
        return True

    finally:
        # Clean up temp file
        if os.path.exists(financial_file_path):
            os.unlink(financial_file_path)

def test_generic_dataset_still_works():
    """Test that the application still works with generic/unclassified data"""
    print("Testing Generic Dataset Behavior...")

    # Create completely generic dataset with no obvious domain indicators
    generic_data = pd.DataFrame({
        'col1': [1, 2, 3, 4, 5],
        'col2': ['A', 'B', 'A', 'C', 'B'],
        'col3': [10.5, 20.3, 15.7, 18.9, 22.1],
        'col4': ['X', 'Y', 'X', 'Z', 'Y'],
        'col5': [100, 200, 150, 180, 220]
    })

    # Add a date column for time series capability
    generic_data['date_col'] = pd.date_range('2023-01-01', periods=5, freq='D')

    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        generic_data.to_csv(f.name, index=False)
        generic_file_path = f.name

    try:
        # Load dataset through DataManager (simulating upload)
        from src.ingestion.data_loader import DataLoader
        df = DataLoader.load_data(generic_file_path)
        DataManager.store_dataset(df)

        # Get dataset intelligence
        intelligence = DataManager.get_dataset_intelligence()

        print("Dataset Type Detected:", intelligence.get('dataset_type'))
        print("Entity Type:", intelligence.get('entity_type'))
        print("Description:", intelligence.get('description')[:100] + "...")

        # Should be classified as generic
        assert intelligence.get('dataset_type') == 'generic', f"Expected 'generic', got {intelligence.get('dataset_type')}"
        assert intelligence.get('entity_type') == 'records', f"Expected 'records', got {intelligence.get('entity_type')}"

        # Should still provide useful intelligence even for generic data
        assert len(intelligence.get('important_metrics', [])) > 0, "No important metrics found for generic data"
        assert len(intelligence.get('important_dimensions', [])) > 0, "No important dimensions found for generic data"
        assert intelligence.get('time_column') == 'date_col', f"Expected 'date_col', got {intelligence.get('time_column')}"
        assert len(intelligence.get('page_names', [])) > 0, "No page names generated for generic data"
        assert len(intelligence.get('suggested_questions', [])) > 0, "No suggested questions generated for generic data"
        assert len(intelligence.get('suggested_actions', [])) > 0, "No suggested actions generated for generic data"

        print("Generic Dataset Behavior Test PASSED\n")
        return True

    finally:
        # Clean up temp file
        if os.path.exists(generic_file_path):
            os.unlink(generic_file_path)

if __name__ == "__main__":
    # Import DataLoader here to avoid issues
    from src.ingestion.data_loader import DataLoader

    print("=" * 60)
    print("TESTING DATASET-DRIVEN BEHAVIOR OF AI BUSINESS ANALYST")
    print("=" * 60)

    # Run all tests
    test_hr_dataset_driven_behavior()
    test_retail_dataset_driven_behavior()
    test_financial_dataset_driven_behavior()
    test_generic_dataset_still_works()

    print("=" * 60)
    print("ALL DATASET-DRIVEN BEHAVIOR TESTS PASSED!")
    print("The application successfully adapts to different dataset types.")
    print("=" * 60)