import io

import pandas as pd


def summarize_csv(content: bytes) -> tuple[pd.DataFrame, str]:
    data = pd.read_csv(io.BytesIO(content))
    row_count, col_count = data.shape
    numeric_columns = data.select_dtypes(include=["number"]).columns.tolist()

    summary_lines = [
        f"Rows: {row_count}",
        f"Columns: {col_count}",
        f"Numeric columns: {', '.join(numeric_columns) if numeric_columns else 'None'}",
    ]

    if numeric_columns:
        describe = data[numeric_columns].describe().round(2)
        for column in numeric_columns[:5]:
            summary_lines.append(
                f"{column}: mean={describe.at['mean', column]}, std={describe.at['std', column]}, max={describe.at['max', column]}"
            )
    else:
        summary_lines.append("No numeric data available for KPI analysis.")

    return data, "\n".join(summary_lines)
