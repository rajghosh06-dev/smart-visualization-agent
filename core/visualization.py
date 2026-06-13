import plotly.express as px
import pandas as pd
import json

# Custom neon colors for cyber-professional theme
NEON_COLORS = ["#00f2fe", "#8a2be2", "#00ffd2", "#f20089", "#ffb700", "#39ff14"]

def generate_chart(df: pd.DataFrame, parsed: dict):
    """
    Generates a Plotly figure from a DataFrame and parsed chart settings.
    Applies custom styling to match the Cyber-Professional dashboard theme.
    """
    chart_type = parsed.get("chart_type", "bar")
    x = parsed.get("x")
    y = parsed.get("y")
    
    # 1. Fallback / Validation
    if not x:
        # If no X column is resolved, use the first column in the dataframe
        x = df.columns[0]
        
    # Standardize Y
    if y is None and chart_type != "histogram":
        # Find the first numeric column that is not X
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        remaining_numeric = [c for c in numeric_cols if c != x]
        if remaining_numeric:
            y = remaining_numeric[0]
        else:
            y = df.columns[-1]

    # Clean data (e.g. handle NaNs to prevent empty plots)
    clean_df = df.copy()
    
    # 2. Build Figures based on chart_type
    fig = None
    title = f"{chart_type.title()} Chart: "
    if isinstance(y, list):
        title += f"{', '.join(y)} vs {x}"
    elif y:
        title += f"{y} vs {x}"
    else:
        title += f"Distribution of {x}"

    if chart_type == "bar":
        fig = px.bar(
            clean_df, 
            x=x, 
            y=y, 
            barmode="group",
            title=title,
            color_discrete_sequence=NEON_COLORS
        )
    elif chart_type == "line":
        fig = px.line(
            clean_df, 
            x=x, 
            y=y, 
            title=title,
            color_discrete_sequence=NEON_COLORS
        )
    elif chart_type == "scatter":
        fig = px.scatter(
            clean_df, 
            x=x, 
            y=y, 
            title=title,
            color_discrete_sequence=NEON_COLORS
        )
    elif chart_type == "histogram":
        fig = px.histogram(
            clean_df, 
            x=x, 
            title=title,
            color_discrete_sequence=NEON_COLORS,
            nbins=30
        )
    elif chart_type == "pie":
        # For pie charts, only support single series
        pie_y = y[0] if isinstance(y, list) else y
        fig = px.pie(
            clean_df, 
            names=x, 
            values=pie_y, 
            title=title,
            color_discrete_sequence=NEON_COLORS
        )
    else:
        # Default bar chart fallback
        fig = px.bar(
            clean_df, 
            x=x, 
            y=y, 
            title=title,
            color_discrete_sequence=NEON_COLORS
        )

    # 3. Apply Cyber-Professional Dark Styling
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Transparent background for glassmorphic card fit
        plot_bgcolor="rgba(15, 23, 42, 0.4)",  # Deep slate overlay
        font=dict(
            family="Inter, system-ui, -apple-system, sans-serif",
            size=12,
            color="#e2e8f0"  # High contrast grey-white
        ),
        title=dict(
            font=dict(size=16, color="#00f2fe", weight="bold"),
            pad=dict(b=10),
            x=0.02
        ),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.6)",
            bordercolor="rgba(255, 255, 255, 0.1)",
            borderwidth=1,
            font=dict(color="#cbd5e1")
        ),
        margin=dict(l=50, r=30, t=70, b=50),
        hoverlabel=dict(
            bgcolor="#1e1e2f",
            font_size=12,
            font_family="Inter, sans-serif"
        )
    )

    # Gridlines and zero-lines styling
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.12)",
        tickfont=dict(color="#94a3b8"),
        title_font=dict(color="#cbd5e1")
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.12)",
        tickfont=dict(color="#94a3b8"),
        title_font=dict(color="#cbd5e1")
    )

    return fig
