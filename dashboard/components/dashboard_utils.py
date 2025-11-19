"""
Dashboard Components
Reusable components for the Streamlit dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import numpy as np

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )

def create_kpi_row(kpis):
    """Create a row of KPI metrics"""
    if not kpis:
        return
    
    num_kpis = len(kpis)
    cols = st.columns(num_kpis)
    
    for i, (title, value, delta) in enumerate(kpis):
        with cols[i]:
            st.metric(title, value, delta)

def create_data_table_with_search(df, title="Data Table", key_prefix="table"):
    """Create a data table with search functionality"""
    st.subheader(title)
    
    # Search functionality
    search_term = st.text_input(f"Search {title}", key=f"{key_prefix}_search")
    
    if search_term:
        # Search across all string columns
        string_columns = df.select_dtypes(include=['object']).columns
        mask = df[string_columns].astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    # Display results count
    st.write(f"Showing {len(filtered_df):,} of {len(df):,} records")
    
    # Display table
    st.dataframe(filtered_df, use_container_width=True)
    
    return filtered_df

def create_download_button(data, filename, button_text="Download CSV"):
    """Create a download button for dataframes"""
    csv = data.to_csv(index=False)
    st.download_button(
        label=button_text,
        data=csv,
        file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )

def create_status_indicator(status, label="Status"):
    """Create a colored status indicator"""
    if status == "success" or status == "healthy":
        st.success(f"✅ {label}: Healthy")
    elif status == "warning":
        st.warning(f"⚠️ {label}: Warning")
    elif status == "error" or status == "critical":
        st.error(f"🔴 {label}: Critical")
    else:
        st.info(f"ℹ️ {label}: {status}")

def create_trend_chart(data, x_col, y_col, title="Trend Analysis"):
    """Create a trend line chart"""
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        title=title,
        markers=True
    )
    
    fig.update_layout(
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title()
    )
    
    return fig

def create_comparison_bar_chart(data, x_col, y_col, title="Comparison Chart", orientation='v'):
    """Create a comparison bar chart"""
    if orientation == 'h':
        fig = px.bar(
            data,
            x=y_col,
            y=x_col,
            orientation='h',
            title=title
        )
    else:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title
        )
    
    return fig

def create_distribution_chart(data, column, title="Distribution Analysis"):
    """Create a distribution histogram"""
    fig = px.histogram(
        data,
        x=column,
        title=title,
        nbins=30
    )
    
    # Add mean line
    mean_val = data[column].mean()
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: {mean_val:.2f}"
    )
    
    return fig

def create_correlation_heatmap(data, title="Correlation Matrix"):
    """Create a correlation heatmap for numeric columns"""
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) < 2:
        st.warning("Not enough numeric columns for correlation analysis")
        return None
    
    corr_matrix = data[numeric_cols].corr()
    
    fig = px.imshow(
        corr_matrix,
        title=title,
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1
    )
    
    return fig

def create_geographic_map(data, lat_col, lon_col, color_col=None, title="Geographic Distribution"):
    """Create a geographic scatter map"""
    if color_col:
        fig = px.scatter_mapbox(
            data,
            lat=lat_col,
            lon=lon_col,
            color=color_col,
            title=title,
            mapbox_style="open-street-map",
            zoom=3
        )
    else:
        fig = px.scatter_mapbox(
            data,
            lat=lat_col,
            lon=lon_col,
            title=title,
            mapbox_style="open-street-map",
            zoom=3
        )
    
    return fig

def create_gauge_chart(value, title="Gauge", min_val=0, max_val=100, threshold=None):
    """Create a gauge chart for KPIs"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val * 0.6], 'color': "lightgray"},
                {'range': [max_val * 0.6, max_val * 0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold or max_val * 0.9
            }
        }
    ))
    
    return fig

def create_summary_stats_card(data, column, title=None):
    """Create a summary statistics card"""
    if title is None:
        title = f"{column.replace('_', ' ').title()} Statistics"
    
    st.subheader(title)
    
    if data[column].dtype in ['int64', 'float64']:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean", f"{data[column].mean():.2f}")
        with col2:
            st.metric("Median", f"{data[column].median():.2f}")
        with col3:
            st.metric("Min", f"{data[column].min():.2f}")
        with col4:
            st.metric("Max", f"{data[column].max():.2f}")
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric("Std Dev", f"{data[column].std():.2f}")
        with col6:
            st.metric("25th %ile", f"{data[column].quantile(0.25):.2f}")
        with col7:
            st.metric("75th %ile", f"{data[column].quantile(0.75):.2f}")
        with col8:
            st.metric("Count", f"{data[column].count()}")
    
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Unique Values", data[column].nunique())
        with col2:
            st.metric("Most Frequent", data[column].mode().iloc[0] if not data[column].mode().empty else "N/A")
        with col3:
            st.metric("Null Count", data[column].isnull().sum())

def create_filter_sidebar(data, filterable_columns):
    """Create a sidebar with multiple filters"""
    st.sidebar.subheader("🔧 Filters")
    
    filters = {}
    
    for col in filterable_columns:
        if data[col].dtype == 'object':
            # Categorical filter
            unique_vals = data[col].unique()
            selected_vals = st.sidebar.multiselect(
                f"Filter {col.replace('_', ' ').title()}",
                options=unique_vals,
                default=unique_vals
            )
            filters[col] = selected_vals
        
        elif data[col].dtype in ['int64', 'float64']:
            # Numeric range filter
            min_val = float(data[col].min())
            max_val = float(data[col].max())
            
            selected_range = st.sidebar.slider(
                f"{col.replace('_', ' ').title()} Range",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val)
            )
            filters[col] = selected_range
    
    return filters

def apply_filters(data, filters):
    """Apply filters to dataframe"""
    filtered_data = data.copy()
    
    for col, filter_val in filters.items():
        if isinstance(filter_val, list):
            # Categorical filter
            filtered_data = filtered_data[filtered_data[col].isin(filter_val)]
        elif isinstance(filter_val, tuple):
            # Numeric range filter
            min_val, max_val = filter_val
            filtered_data = filtered_data[
                (filtered_data[col] >= min_val) & 
                (filtered_data[col] <= max_val)
            ]
    
    return filtered_data

def create_alert_box(message, alert_type="info"):
    """Create styled alert boxes"""
    if alert_type == "success":
        st.success(message)
    elif alert_type == "warning":
        st.warning(message)
    elif alert_type == "error":
        st.error(message)
    else:
        st.info(message)

def format_number(value, format_type="currency"):
    """Format numbers for display"""
    if format_type == "currency":
        return f"${value:,.2f}"
    elif format_type == "percentage":
        return f"{value:.1f}%"
    elif format_type == "integer":
        return f"{int(value):,}"
    elif format_type == "decimal":
        return f"{value:,.2f}"
    else:
        return str(value)