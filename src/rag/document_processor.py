import pandas as pd
import numpy as np

def convert_dataframe_to_chunks(df: pd.DataFrame, dataset_name="dataset", rows_per_chunk=10) -> list[dict]:
    """
    Transform a pandas DataFrame into natural language text chunks for semantic indexing.
    Returns a list of dicts: [{"text": str, "metadata": dict}]
    """
    chunks = []
    num_rows = len(df)

    # Chunk 0: Schema and Structure Summary
    schema_text = f"Dataset: {dataset_name}\n"
    schema_text += f"Total Rows: {num_rows}, Total Columns: {len(df.columns)}\n"
    schema_text += "Columns and Types:\n"
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        # Add more meaningful description for common types
        if 'int' in dtype_str or 'float' in dtype_str:
            type_desc = "numeric"
        elif 'object' in dtype_str or 'string' in dtype_str:
            type_desc = "text/categorical"
        elif 'bool' in dtype_str:
            type_desc = "boolean"
        elif 'datetime' in dtype_str:
            type_desc = "date/time"
        else:
            type_desc = dtype_str
        schema_text += f"- {col} ({type_desc})\n"

    chunks.append({
        "text": schema_text,
        "metadata": {"source": "schema_summary", "dataset": dataset_name}
    })

    # Chunk 1: General Summary Stats for Numeric Columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        stats_text = f"Statistical Summary of {dataset_name} (Numeric Columns):\n"
        for col in numeric_cols:
            col_min = df[col].min()
            col_max = df[col].max()
            col_mean = df[col].mean()
            col_std = df[col].std()
            stats_text += f"- Column '{col}': Min = {col_min:.2f}, Max = {col_max:.2f}, Average = {col_mean:.2f}, Std Dev = {col_std:.2f}\n"

        chunks.append({
            "text": stats_text,
            "metadata": {"source": "numeric_stats_summary", "dataset": dataset_name}
        })

    # Chunk 2: Summary for Categorical/Text Columns
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns
    categorical_cols = [col for col in categorical_cols if df[col].nunique() < min(50, len(df) // 2)]  # Only truly categorical
    if len(categorical_cols) > 0:
        cat_text = f"Categorical Summary of {dataset_name}:\n"
        for col in categorical_cols[:5]:  # Limit to first 5 to avoid huge chunks
            unique_count = df[col].nunique()
            top_value = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
            top_freq = df[col].value_counts().iloc[0] if not df[col].value_counts().empty else 0
            cat_text += f"- Column '{col}': {unique_count} unique values, Most frequent: '{top_value}' ({top_freq} occurrences)\n"

        chunks.append({
            "text": cat_text,
            "metadata": {"source": "categorical_summary", "dataset": dataset_name}
        })

    # Chunk 3: Date/Time Column Summary (if any)
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols) > 0:
        date_text = f"Date/Time Summary of {dataset_name}:\n"
        for col in date_cols:
            if not df[col].isna().all():
                min_date = df[col].min()
                max_date = df[col].max()
                date_text += f"- Column '{col}': Range from {min_date} to {max_date}\n"
            else:
                date_text += f"- Column '{col}': All values are null\n"

        chunks.append({
            "text": date_text,
            "metadata": {"source": "date_summary", "dataset": dataset_name}
        })

    # Chunk 4: Correlation Information (for numeric columns with sufficient data)
    if len(numeric_cols) >= 2:
        # Calculate correlations only if we have enough non-null data
        numeric_df = df[numeric_cols].dropna()
        if len(numeric_df) >= 2:
            corr_matrix = numeric_df.corr()
            # Find strong correlations (absolute value > 0.5)
            strong_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:
                        strong_correlations.append((col1, col2, corr_value))

            if strong_correlations:
                corr_text = f"Strong Correlations in {dataset_name} (|r| > 0.5):\n"
                for col1, col2, corr_value in strong_correlations[:10]:  # Limit to top 10
                    corr_text += f"- {col1} ↔ {col2}: {corr_value:.3f}\n"

                chunks.append({
                    "text": corr_text,
                    "metadata": {"source": "correlation_summary", "dataset": dataset_name}
                })

    # Chunk 5+: Row Chunks with Enhanced Descriptions
    # Instead of just listing all fields, create more meaningful descriptions
    for start_idx in range(0, num_rows, rows_per_chunk):
        end_idx = min(start_idx + rows_per_chunk, num_rows)
        sub_df = df.iloc[start_idx:end_idx]

        chunk_text = f"Records {start_idx + 1} to {end_idx} in {dataset_name}:\n"
        for idx, row in sub_df.iterrows():
            # Create a more natural language description
            row_parts = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    row_parts.append(f"{col} is not available")
                elif isinstance(val, (int, float)) and not pd.isna(val):
                    row_parts.append(f"{col} is {val}")
                else:
                    row_parts.append(f"{col} is '{val}'")

            # Join with commas and "and" for the last item for better readability
            if len(row_parts) == 1:
                row_desc = row_parts[0]
            elif len(row_parts) == 2:
                row_desc = " and ".join(row_parts)
            else:
                row_desc = ", ".join(row_parts[:-1]) + ", and " + row_parts[-1]

            chunk_text += f"- Row {idx + 1}: {row_desc}.\n"

        chunks.append({
            "text": chunk_text,
            "metadata": {
                "source": "data_rows",
                "dataset": dataset_name,
                "start_row": start_idx + 1,
                "end_row": end_idx
            }
        })

    return chunks
