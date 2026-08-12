"""
Dataset Intelligence Layer for determining dataset context and generating
dynamic UI elements based on the actual dataset content.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import pandas as pd

from src.schema.dataset_understanding import understand_dataset
from src.schema.schema_analyzer import analyze_schema


@dataclass
class DatasetIntelligence:
    """Container for dataset intelligence information."""
    dataset_type: str  # e.g., 'retail', 'healthcare', 'hr', 'finance', 'logistics'
    entity_type: str   # e.g., 'customers', 'patients', 'employees', 'transactions'
    entity_name_singular: str  # e.g., 'customer', 'patient', 'employee'
    description: str   # Human-readable description of what the dataset represents

    # Column intelligence
    column_display_names: Dict[str, str]  # Original -> Friendly name
    column_descriptions: Dict[str, str]   # Original -> Description of what it represents
    important_metrics: List[str]          # Columns that are key measurements
    important_dimensions: List[str]       # Columns good for grouping/categorization
    time_column: Optional[str]            # Primary date/time column if exists

    # Analysis capabilities
    available_analyses: List[str]         # What types of analysis make sense
    recommended_analyses: List[str]       # Which analyses to prioritize

    # UI Intelligence
    page_names: List[str]                 # Suggested page/section names
    kpis: List[Dict[str, str]]            # Key Performance Indicators to show
    chart_suggestions: List[Dict[str, str]] # Recommended charts
    terminology: Dict[str, str]           # Domain-specific terms to use

    # Suggested interactions
    suggested_questions: List[str]        # Questions users might want to ask
    suggested_actions: List[str]          # Actions to recommend


class DatasetIntelligenceEngine:
    """Engine for generating dataset intelligence from a dataframe."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.schema = analyze_schema(df)
        self.basic_understanding = understand_dataset(df, self.schema)

    def generate_intelligence(self) -> DatasetIntelligence:
        """Generate comprehensive dataset intelligence."""
        # Detect dataset type and entity
        dataset_type, entity_type, entity_name_singular = self._detect_dataset_type()

        # Generate column intelligence
        column_display_names, column_descriptions = self._generate_column_intelligence()

        # Identify important metrics and dimensions
        important_metrics, important_dimensions, time_column = self._identify_important_columns()

        # Determine available and recommended analyses
        available_analyses, recommended_analyses = self._determine_analyses()

        # Generate UI intelligence
        page_names = self._generate_page_names(dataset_type, entity_type)
        kpis = self._generate_kpis(important_metrics, dataset_type)
        chart_suggestions = self._generate_chart_suggestions(important_metrics, important_dimensions, time_column)
        terminology = self._generate_terminology(dataset_type, entity_type)

        # Generate suggestions
        suggested_questions = self._generate_suggested_questions(dataset_type, entity_type, important_metrics, important_dimensions)
        suggested_actions = self._generate_suggested_actions(dataset_type, entity_type)

        # Create description
        description = self._generate_description(dataset_type, entity_type)

        return DatasetIntelligence(
            dataset_type=dataset_type,
            entity_type=entity_type,
            entity_name_singular=entity_name_singular,
            description=description,
            column_display_names=column_display_names,
            column_descriptions=column_descriptions,
            important_metrics=important_metrics,
            important_dimensions=important_dimensions,
            time_column=time_column,
            available_analyses=available_analyses,
            recommended_analyses=recommended_analyses,
            page_names=page_names,
            kpis=kpis,
            chart_suggestions=chart_suggestions,
            terminology=terminology,
            suggested_questions=suggested_questions,
            suggested_actions=suggested_actions
        )

    def _detect_dataset_type(self) -> tuple[str, str, str]:
        """Detect what type of dataset this is and what entities it contains."""
        # Domain detection keywords
        domain_indicators = {
            'retail': {
                'keywords': ['sales', 'revenue', 'product', 'customer', 'order', 'purchase', 'store', 'inventory', 'price', 'amount', 'quantity', 'store_id', 'product_id'],
                'entity': 'customers',
                'entity_singular': 'customer'
            },
            'healthcare': {
                'keywords': ['patient', 'diagnosis', 'treatment', 'medication', 'doctor', 'hospital', 'clinic', 'health', 'medical', 'blood', 'pressure', 'temperature', 'weight', 'height'],
                'entity': 'patients',
                'entity_singular': 'patient'
            },
            'hr': {
                'keywords': ['employee', 'salary', 'department', 'position', 'hire', 'performance', 'review', 'benefits', 'payroll', 'manager', 'staff', 'workforce'],
                'entity': 'employees',
                'entity_singular': 'employee'
            },
            'finance': {
                'keywords': ['transaction', 'amount', 'balance', 'account', 'payment', 'invoice', 'expense', 'income', 'budget', 'cost', 'revenue', 'profit', 'loss', 'credit', 'debit'],
                'entity': 'transactions',
                'entity_singular': 'transaction'
            },
            'logistics': {
                'keywords': ['shipment', 'delivery', 'route', 'warehouse', 'inventory', 'supply', 'transport', 'shipping', 'tracking', 'destination', 'origin', 'carrier', 'freight'],
                'entity': 'shipments',
                'entity_singular': 'shipment'
            },
            'education': {
                'keywords': ['student', 'course', 'grade', 'score', 'exam', 'assignment', 'teacher', 'class', 'enrollment', 'graduation', 'attendance'],
                'entity': 'students',
                'entity_singular': 'student'
            },
            'marketing': {
                'keywords': ['campaign', 'click', 'impression', 'conversion', 'lead', 'ad', 'marketing', 'promotion', 'email', 'social', 'engagement', 'ctr', 'roi'],
                'entity': 'campaigns',
                'entity_singular': 'campaign'
            }
        }

        # Get all column names as lowercase text
        column_text = ' '.join([col.lower() for col in self.df.columns])

        # Also check some sample values for textual columns
        sample_text = ""
        for col in self.schema.get('text_columns', [])[:3]:  # Check first 3 text columns
            if col in self.df.columns:
                sample_values = self.df[col].dropna().head(10).astype(str).str.lower()
                sample_text += ' ' + ' '.join(sample_values)

        combined_text = column_text + ' ' + sample_text

        # Score each domain
        domain_scores = {}
        for domain, info in domain_indicators.items():
            score = 0
            for keyword in info['keywords']:
                if keyword in combined_text:
                    score += 1
            domain_scores[domain] = score

        # Find best matching domain
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:  # At least some match
                domain_info = domain_indicators[best_domain]
                return best_domain, domain_info['entity'], domain_info['entity_singular']

        # Default to generic
        return 'generic', 'records', 'record'

    def _generate_column_intelligence(self) -> tuple[Dict[str, str], Dict[str, str]]:
        """Generate friendly display names and descriptions for columns."""
        display_names = {}
        descriptions = {}

        # Common column name mappings
        common_mappings = {
            # ID columns
            'id': 'ID',
            'customer_id': 'Customer ID',
            'employee_id': 'Employee ID',
            'patient_id': 'Patient ID',
            'product_id': 'Product ID',
            'order_id': 'Order ID',
            'transaction_id': 'Transaction ID',

            # Name columns
            'name': 'Name',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'full_name': 'Full Name',

            # Date columns
            'date': 'Date',
            'created_date': 'Created Date',
            'hire_date': 'Hire Date',
            'birth_date': 'Birth Date',
            'transaction_date': 'Transaction Date',

            # Amount/value columns
            'amount': 'Amount',
            'price': 'Price',
            'salary': 'Salary',
            'revenue': 'Revenue',
            'cost': 'Cost',
            'total': 'Total',
            'value': 'Value',

            # Quantity columns
            'quantity': 'Quantity',
            'qty': 'Quantity',
            'count': 'Count',

            # Category columns
            'category': 'Category',
            'department': 'Department',
            'type': 'Type',
            'status': 'Status',
            'level': 'Level',

            # Location columns
            'city': 'City',
            'state': 'State',
            'country': 'Country',
            'address': 'Address',
            'zipcode': 'ZIP Code',
            'postal_code': 'Postal Code',

            # Contact columns
            'email': 'Email',
            'phone': 'Phone Number',
            'telephone': 'Telephone Number',
        }

        for col in self.df.columns:
            # Generate display name
            display_name = common_mappings.get(col.lower(), col.replace('_', ' ').title())
            display_names[col] = display_name

            # Generate description based on column type and sample data
            description = self._generate_column_description(col)
            descriptions[col] = description

        return display_names, descriptions

    def _generate_column_description(self, column: str) -> str:
        """Generate a description of what a column represents."""
        col_lower = column.lower()
        series = self.df[column]

        # Check if it's an ID column
        if 'id' in col_lower or column in self.schema.get('id_columns', []):
            return f"Unique identifier for each {self.basic_understanding.get('entity_name_singular', 'record')}"

        # Check if it's a date column
        if column in self.schema.get('date_columns', []):
            return f"Date and time information"

        # Check if it's a numeric column
        if column in self.schema.get('numeric_columns', []):
            # Try to determine what kind of numeric value it is
            if any(word in col_lower for word in ['price', 'cost', 'amount', 'salary', 'revenue', 'value']):
                return f"Monetary value or price"
            elif any(word in col_lower for word in ['quantity', 'qty', 'count', 'number']):
                return f"Quantity or count"
            elif any(word in col_lower for word in ['score', 'rating', 'percentage']):
                return f"Score or rating value"
            else:
                return f"Numerical measurement"

        # Check if it's a categorical column
        if column in self.schema.get('categorical_columns', []):
            unique_count = series.nunique()
            if unique_count <= 5:
                return f"Category with {unique_count} possible values"
            else:
                return f"Category or classification"

        # Check if it's a text column
        if column in self.schema.get('text_columns', []):
            avg_length = series.astype(str).str.len().mean()
            if avg_length > 100:
                return f"Detailed text or description"
            else:
                return f"Short text or label"

        # Default
        return f"Data field containing information"

    def _identify_important_columns(self) -> tuple[List[str], List[str], Optional[str]]:
        """Identify important metrics, dimensions, and time column."""
        important_metrics = []
        important_dimensions = []
        time_column = None

        # Identify time column (prefer the one with best data quality)
        date_cols = self.schema.get('date_columns', [])
        if date_cols:
            # Pick the date column with most non-null values
            best_date_col = max(date_cols, key=lambda col: self.df[col].notna().sum())
            time_column = best_date_col

        # Identify important metrics (numeric columns that aren't IDs)
        numeric_cols = self.schema.get('numeric_columns', [])
        id_cols = set(self.schema.get('id_columns', []))

        for col in numeric_cols:
            if col not in id_cols:
                # Check if it looks like a meaningful metric
                col_lower = col.lower()
                if any(word in col_lower for word in ['amount', 'price', 'cost', 'revenue', 'sales', 'profit',
                                                     'salary', 'value', 'total', 'score', 'rating', 'count',
                                                     'quantity', 'qty', 'percentage', 'rate']):
                    important_metrics.append(col)
                else:
                    # Still consider it if it has good variation
                    if self.df[col].std() > 0 and self.df[col].notna().sum() > len(self.df) * 0.5:
                        important_metrics.append(col)

        # Identify important dimensions (categorical columns good for grouping)
        categorical_cols = self.schema.get('categorical_columns', [])
        boolean_cols = self.schema.get('boolean_columns', [])

        for col in categorical_cols + boolean_cols:
            # Good for grouping if not too many unique values and not an ID
            if col not in id_cols:
                unique_count = self.df[col].nunique()
                total_count = len(self.df)
                if unique_count > 1 and unique_count < total_count * 0.8:  # Not too unique, not too few
                    important_dimensions.append(col)

        # Add date column as dimension if we have one
        if time_column and time_column not in important_dimensions:
            important_dimensions.append(time_column)

        return important_metrics, important_dimensions, time_column

    def _determine_analyses(self) -> tuple[List[str], List[str]]:
        """Determine what analyses are available and recommended."""
        available = []
        recommended = []

        # Basic analytics
        if len(self.basic_understanding.get('candidate_metrics', [])) > 0:
            available.append('basic_analytics')
            recommended.append('basic_analytics')

        # Group analysis
        if len(self.basic_understanding.get('candidate_dimensions', [])) > 0:
            available.append('group_analysis')
            recommended.append('group_analysis')

        # Correlation analysis
        if len(self.schema.get('numeric_columns', [])) >= 2:
            available.append('correlation_analysis')
            recommended.append('correlation_analysis')

        # Time series analysis
        if self.basic_understanding.get('capabilities', {}).get('forecasting', False):
            available.append('time_series_analysis')
            available.append('forecasting')
            recommended.append('time_series_analysis')

        # Anomaly detection
        if self.basic_understanding.get('capabilities', {}).get('anomaly_detection', False):
            available.append('anomaly_detection')
            recommended.append('anomaly_detection')

        # Record lookup
        if self.basic_understanding.get('capabilities', {}).get('record_lookup', False):
            available.append('record_lookup')

        # Text analysis (if we have text columns)
        if len(self.schema.get('text_columns', [])) > 0:
            available.append('text_analysis')

        return available, recommended

    def _generate_page_names(self, dataset_type: str, entity_type: str) -> List[str]:
        """Generate suggested page/section names based on dataset type."""
        # Base pages that are generally useful
        base_pages = ["Overview"]

        # Type-specific pages
        type_pages = {
            'retail': ["Sales Performance", "Products", "Customers", "Store Analysis", "Trends"],
            'healthcare': ["Patient Demographics", "Treatment Patterns", "Health Outcomes", "Visits", "Risk Factors"],
            'hr': ["Employee Demographics", "Compensation", "Department Analysis", "Performance", "Hire Trends"],
            'finance': ["Transaction Summary", "Income & Expenses", "Accounts", "Trends", "Financial Health"],
            'logistics': ["Shipment Tracking", "Delivery Performance", "Routes", "Inventory", "Cost Analysis"],
            'education': ["Student Performance", "Course Analysis", "Grades", "Attendance", "Demographics"],
            'marketing': ["Campaign Performance", "Channel Analysis", "Customer Journey", "Conversion", "Engagement"],
            'generic': ["Data Exploration", "Patterns", "Comparisons", "Trends", "Outliers"]
        }

        specific_pages = type_pages.get(dataset_type, type_pages['generic'])

        # Combine and limit to reasonable number
        all_pages = base_pages + specific_pages
        return all_pages[:6]  # Limit to 6 pages

    def _generate_kpis(self, important_metrics: List[str], dataset_type: str) -> List[Dict[str, str]]:
        """Generate KPI suggestions based on important metrics and dataset type."""
        kpis = []

        # If we have important metrics, create KPIs for them
        for metric in important_metrics[:4]:  # Limit to top 4
            kpis.append({
                'column': metric,
                'display_name': metric.replace('_', ' ').title(),
                'calculation': 'sum' if any(word in metric.lower() for word in ['amount', 'price', 'cost', 'revenue', 'sales']) else 'average',
                'format': 'currency' if any(word in metric.lower() for word in ['amount', 'price', 'cost', 'revenue', 'cost']) else 'number'
            })

        # If no good metrics found, provide generic ones
        if not kpis:
            numeric_cols = self.schema.get('numeric_columns', [])
            id_cols = set(self.schema.get('id_columns', []))
            for col in numeric_cols[:3]:
                if col not in id_cols:
                    kpis.append({
                        'column': col,
                        'display_name': col.replace('_', ' ').title(),
                        'calculation': 'average',
                        'format': 'number'
                    })

        return kpis

    def _generate_chart_suggestions(self, important_metrics: List[str], important_dimensions: List[str],
                                  time_column: Optional[str]) -> List[Dict[str, str]]:
        """Generate chart suggestions based on available data."""
        charts = []

        # Time series charts
        if time_column and important_metrics:
            for metric in important_metrics[:2]:
                charts.append({
                    'type': 'line',
                    'title': f"{metric.replace('_', ' ').title()} Over Time",
                    'x_axis': time_column,
                    'y_axis': metric,
                    'description': f"Shows how {metric.replace('_', ' ')} changes over time"
                })

        # Bar charts (metric by dimension)
        if important_metrics and important_dimensions:
            for metric in important_metrics[:2]:
                for dimension in important_dimensions[:2]:
                    if dimension != time_column:  # Avoid duplicate time charts
                        charts.append({
                            'type': 'bar',
                            'title': f"{metric.replace('_', ' ').title()} by {dimension.replace('_', ' ').title()}",
                            'x_axis': dimension,
                            'y_axis': metric,
                            'description': f"Compares {metric.replace('_', ' ')} across different {dimension.replace('_', ' ')} values"
                        })

        # Scatter plots (correlations)
        if len(important_metrics) >= 2:
            for i, metric1 in enumerate(important_metrics[:2]):
                for metric2 in important_metrics[:2]:
                    if i != important_metrics.index(metric2):  # Different metrics
                        charts.append({
                            'type': 'scatter',
                            'title': f"{metric1.replace('_', ' ').title()} vs {metric2.replace('_', ' ').title()}",
                            'x_axis': metric1,
                            'y_axis': metric2,
                            'description': f"Shows relationship between {metric1.replace('_', ' ')} and {metric2.replace('_', ' ')}"
                        })

        # Distribution charts
        for metric in important_metrics[:2]:
            charts.append({
                'type': 'histogram',
                'title': f"Distribution of {metric.replace('_', ' ').title()}",
                'x_axis': metric,
                'description': f"Shows the distribution of values for {metric.replace('_', ' ')}"
            })

        # Limit charts to avoid overwhelming
        return charts[:6]

    def _generate_terminology(self, dataset_type: str, entity_type: str) -> Dict[str, str]:
        """Generate domain-specific terminology to use instead of generic terms."""
        # Base terminology replacements
        base_terms = {
            'analysis': 'review',
            'metric': 'measurement',
            'dimension': 'category',
            'record': entity_type[:-1] if entity_type.endswith('s') else entity_type,  # Simple plural removal
            'dataset': f'{entity_type} data'
        }

        # Type-specific terminology
        type_terms = {
            'retail': {
                'analysis': 'sales review',
                'performance': 'sales performance',
                'trend': 'sales trend',
                'customer': 'shopper' if 'online' in str(self.df.columns).lower() else 'customer'
            },
            'healthcare': {
                'analysis': 'health review',
                'patient': 'individual',
                'visit': 'encounter',
                'treatment': 'care provided'
            },
            'hr': {
                'analysis': 'workforce review',
                'employee': 'team member',
                'performance': 'work performance',
                'salary': 'compensation'
            },
            'finance': {
                'analysis': 'financial review',
                'transaction': 'financial transaction',
                'amount': 'monetary value',
                'balance': 'account balance'
            }
        }

        # Start with base terms
        terminology = base_terms.copy()

        # Add type-specific terms
        if dataset_type in type_terms:
            terminology.update(type_terms[dataset_type])

        return terminology

    def _generate_suggested_questions(self, dataset_type: str, entity_type: str,
                                    important_metrics: List[str], important_dimensions: List[str]) -> List[str]:
        """Generate suggested questions based on dataset characteristics."""
        questions = []

        # Generic questions
        questions.append(f"What are the most important patterns in this {entity_type} data?")
        questions.append(f"Are there any unusual or exceptional records to investigate?")
        questions.append(f"How complete and reliable is this data?")

        # Metric-specific questions
        if important_metrics:
            top_metric = important_metrics[0]
            questions.append(f"What is the overall summary of {top_metric.replace('_', ' ')}?")

            if len(important_metrics) > 1:
                questions.append(f"How do the different measurements relate to each other?")

        # Dimension-specific questions
        if important_dimensions:
            top_dimension = important_dimensions[0]
            questions.append(f"How does the data break down by {top_dimension.replace('_', ' ')}?")

            if important_metrics and len(important_metrics) > 0:
                metric = important_metrics[0]
                questions.append(f"How does {metric.replace('_', ' ')} vary by {top_dimension.replace('_', ' ')}?")

        # Time-specific questions
        if self.basic_understanding.get('capabilities', {}).get('forecasting', False):
            date_col = self.schema.get('date_columns', [None])[0]
            if date_col and important_metrics:
                metric = important_metrics[0]
                questions.append(f"What trend is visible in {metric.replace('_', ' ')} over time?")
                questions.append(f"What might we expect for {metric.replace('_', ' ')} in the future?")

        # Type-specific questions
        type_questions = {
            'retail': [
                "Which products are performing best?",
                "Who are our most valuable customers?",
                "What are our peak sales periods?"
            ],
            'healthcare': [
                "What are the most common health conditions?",
                "How do patient outcomes vary by treatment?",
                "Are there any concerning health trends?"
            ],
            'hr': [
                "How is compensation distributed across departments?",
                "What factors influence employee performance?",
                "Are there any retention concerns?",
                "How has our workforce changed over time?"
            ],
            'finance': [
                "Where is our money going?",
                "What are our largest expenses?",
                "How is our financial position changing over time?",
                "Are there any unusual transactions?"
            ]
        }

        if dataset_type in type_questions:
            questions.extend(type_questions[dataset_type])

        # Limit and return
        return questions[:8]

    def _generate_suggested_actions(self, dataset_type: str, entity_type: str) -> List[str]:
        """Generate suggested actions based on dataset type."""
        actions = [
            "Review the data quality and address any issues",
            "Look for patterns and trends that could inform decisions",
            "Compare different segments to identify variations"
        ]

        # Type-specific actions
        type_actions = {
            'retail': [
                "Focus on high-performing products and customer segments",
                "Investigate underperforming areas for improvement opportunities",
                "Monitor inventory levels and sales trends"
            ],
            'healthcare': [
                "Identify patients who may need additional care or follow-up",
                "Monitor treatment effectiveness and patient outcomes",
                "Look for patterns that could indicate public health concerns"
            ],
            'hr': [
                "Recognize and reward high-performing employees",
                "Address any compensation disparities or equity concerns",
                "Develop targeted training and development programs"
            ],
            'finance': [
                "Identify cost-saving opportunities",
                "Monitor cash flow and ensure sufficient liquidity",
                "Investigate any unusual or potentially problematic transactions"
            ]
        }

        if dataset_type in type_actions:
            actions.extend(type_actions[dataset_type])

        return actions[:6]

    def _generate_description(self, dataset_type: str, entity_type: str) -> str:
        """Generate a human-readable description of the dataset."""
        descriptions = {
            'retail': f"This dataset contains retail transaction information, including sales, products, and customer data.",
            'healthcare': f"This dataset contains patient health information, including demographics, treatments, and outcomes.",
            'hr': f"This dataset contains human resources information about employees, including demographics, compensation, and performance.",
            'finance': f"This dataset contains financial transaction records, including payments, expenses, and account information.",
            'logistics': f"This dataset contains logistics and supply chain information, including shipments, deliveries, and routing.",
            'education': f"This dataset contains educational information about students, courses, and academic performance.",
            'marketing': f"This dataset contains marketing campaign data, including performance metrics and customer engagement.",
            'generic': f"This dataset contains {entity_type} information with various attributes and measurements."
        }

        return descriptions.get(dataset_type, descriptions['generic'])


def get_dataset_intelligence(df: pd.DataFrame) -> DatasetIntelligence:
    """Convenience function to get dataset intelligence for a dataframe."""
    engine = DatasetIntelligenceEngine(df)
    return engine.generate_intelligence()


def dataset_intelligence_to_dict(intelligence: DatasetIntelligence) -> Dict[str, Any]:
    """Convert DatasetIntelligence to dictionary for easy use in templates/UI."""
    return {
        'dataset_type': intelligence.dataset_type,
        'entity_type': intelligence.entity_type,
        'entity_name_singular': intelligence.entity_name_singular,
        'description': intelligence.description,
        'column_display_names': intelligence.column_display_names,
        'column_descriptions': intelligence.column_descriptions,
        'important_metrics': intelligence.important_metrics,
        'important_dimensions': intelligence.important_dimensions,
        'time_column': intelligence.time_column,
        'available_analyses': intelligence.available_analyses,
        'recommended_analyses': intelligence.recommended_analyses,
        'page_names': intelligence.page_names,
        'kpis': intelligence.kpis,
        'chart_suggestions': intelligence.chart_suggestions,
        'terminology': intelligence.terminology,
        'suggested_questions': intelligence.suggested_questions,
        'suggested_actions': intelligence.suggested_actions
    }