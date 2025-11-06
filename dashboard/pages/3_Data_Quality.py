"""
Data Quality Dashboard Page
Monitor ETL pipeline health and data quality metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Data Quality Dashboard",
    page_icon="🔍",
    layout="wide"
)

def load_data():
    """Load data from session state or redirect to main page"""
    if 'datasets' not in st.session_state:
        st.warning("Please load data from the main dashboard first.")
        st.stop()
    return st.session_state['datasets']

def analyze_data_quality(datasets):
    """Comprehensive data quality analysis"""
    quality_report = {}
    
    for name, df in datasets.items():
        if df is not None and not df.empty:
            # Basic statistics
            total_rows = len(df)
            total_cols = len(df.columns)
            
            # Null analysis
            null_counts = df.isnull().sum()
            null_percentages = (null_counts / total_rows) * 100
            
            # Duplicate analysis
            duplicate_rows = df.duplicated().sum()
            duplicate_percentage = (duplicate_rows / total_rows) * 100
            
            # Data types
            data_types = df.dtypes.value_counts()
            
            # Memory usage
            memory_usage = df.memory_usage(deep=True).sum() / (1024**2)  # MB
            
            quality_report[name] = {
                'total_rows': total_rows,
                'total_cols': total_cols,
                'null_counts': null_counts.to_dict(),
                'null_percentages': null_percentages.to_dict(),
                'duplicate_rows': duplicate_rows,
                'duplicate_percentage': duplicate_percentage,
                'data_types': data_types.to_dict(),
                'memory_usage_mb': memory_usage,
                'completeness_score': ((total_rows * total_cols - null_counts.sum()) / (total_rows * total_cols)) * 100,
                'uniqueness_score': ((total_rows - duplicate_rows) / total_rows) * 100
            }
    
    return quality_report

def create_completeness_chart(quality_report):
    """Create data completeness visualization"""
    datasets = []
    completeness_scores = []
    
    for name, report in quality_report.items():
        datasets.append(name.title())
        completeness_scores.append(report['completeness_score'])
    
    fig = go.Figure()
    
    # Add bars with color coding
    colors = ['red' if score < 90 else 'orange' if score < 95 else 'green' for score in completeness_scores]
    
    fig.add_trace(go.Bar(
        x=datasets,
        y=completeness_scores,
        marker_color=colors,
        text=[f'{score:.1f}%' for score in completeness_scores],
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Data Completeness Score by Dataset',
        xaxis_title='Dataset',
        yaxis_title='Completeness (%)',
        yaxis=dict(range=[0, 100])
    )
    
    # Add threshold lines
    fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Excellent (95%)")
    fig.add_hline(y=90, line_dash="dash", line_color="orange", annotation_text="Good (90%)")
    
    return fig

def create_null_analysis_chart(quality_report):
    """Create null value analysis chart"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=list(quality_report.keys()),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    
    for i, (name, report) in enumerate(quality_report.items()):
        if i >= 4:  # Only show first 4 datasets
            break
        
        null_data = pd.Series(report['null_percentages'])
        null_data = null_data[null_data > 0].sort_values(ascending=False)
        
        if not null_data.empty:
            row, col = positions[i]
            fig.add_trace(
                go.Bar(x=null_data.index, y=null_data.values, name=f'{name} Nulls'),
                row=row, col=col
            )
    
    fig.update_layout(height=600, title_text="Null Value Analysis by Dataset")
    return fig

def create_data_profiling_summary(datasets):
    """Create data profiling summary"""
    profiling_data = []
    
    for name, df in datasets.items():
        if df is not None and not df.empty:
            for column in df.columns:
                col_data = {
                    'dataset': name,
                    'column': column,
                    'dtype': str(df[column].dtype),
                    'null_count': df[column].isnull().sum(),
                    'null_percentage': (df[column].isnull().sum() / len(df)) * 100,
                    'unique_count': df[column].nunique(),
                    'unique_percentage': (df[column].nunique() / len(df)) * 100
                }
                
                # Add specific statistics based on data type
                if df[column].dtype in ['int64', 'float64']:
                    col_data.update({
                        'min_value': df[column].min(),
                        'max_value': df[column].max(),
                        'mean_value': df[column].mean(),
                        'std_value': df[column].std()
                    })
                elif df[column].dtype == 'object':
                    col_data.update({
                        'avg_length': df[column].astype(str).str.len().mean() if not df[column].empty else 0,
                        'max_length': df[column].astype(str).str.len().max() if not df[column].empty else 0
                    })
                
                profiling_data.append(col_data)
    
    return pd.DataFrame(profiling_data)

def create_pipeline_health_metrics():
    """Create mock pipeline health metrics"""
    # In a real implementation, this would connect to actual pipeline logs
    metrics = {
        'last_run': datetime.now() - timedelta(minutes=30),
        'success_rate': 98.5,
        'avg_runtime': 12.3,  # minutes
        'data_freshness': 25,  # minutes since last update
        'error_count': 2,
        'warning_count': 5,
        'processed_records': 15420
    }
    return metrics

def main():
    st.title("🔍 Data Quality Dashboard")
    
    datasets = load_data()
    
    # Pipeline health overview
    st.subheader("⚡ Pipeline Health Status")
    
    health_metrics = create_pipeline_health_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        success_color = "normal" if health_metrics['success_rate'] >= 95 else "off"
        st.metric(
            "Success Rate", 
            f"{health_metrics['success_rate']:.1f}%",
            delta=None
        )
    
    with col2:
        freshness_color = "normal" if health_metrics['data_freshness'] <= 60 else "off"
        st.metric(
            "Data Freshness", 
            f"{health_metrics['data_freshness']} min",
            delta=None
        )
    
    with col3:
        st.metric(
            "Avg Runtime", 
            f"{health_metrics['avg_runtime']:.1f} min",
            delta=None
        )
    
    with col4:
        st.metric(
            "Records Processed", 
            f"{health_metrics['processed_records']:,}",
            delta=None
        )
    
    # Additional health metrics
    col5, col6, col7 = st.columns(3)
    
    with col5:
        st.metric("Errors", health_metrics['error_count'], delta=-1)
    
    with col6:
        st.metric("Warnings", health_metrics['warning_count'], delta=2)
    
    with col7:
        last_run_str = health_metrics['last_run'].strftime('%H:%M')
        st.metric("Last Run", last_run_str, delta=None)
    
    st.divider()
    
    # Data quality analysis
    st.subheader("📊 Data Quality Analysis")
    
    with st.spinner("Analyzing data quality..."):
        quality_report = analyze_data_quality(datasets)
    
    # Completeness overview
    completeness_chart = create_completeness_chart(quality_report)
    st.plotly_chart(completeness_chart, use_container_width=True)
    
    # Quality metrics table
    st.subheader("📋 Quality Metrics Summary")
    
    quality_df = pd.DataFrame([
        {
            'Dataset': name.title(),
            'Rows': report['total_rows'],
            'Columns': report['total_cols'],
            'Completeness (%)': f"{report['completeness_score']:.1f}",
            'Uniqueness (%)': f"{report['uniqueness_score']:.1f}",
            'Duplicates': report['duplicate_rows'],
            'Memory (MB)': f"{report['memory_usage_mb']:.2f}"
        }
        for name, report in quality_report.items()
    ])
    
    st.dataframe(quality_df, use_container_width=True)
    
    # Null value analysis
    st.subheader("🕳️ Missing Data Analysis")
    
    null_chart = create_null_analysis_chart(quality_report)
    st.plotly_chart(null_chart, use_container_width=True)
    
    # Detailed column profiling
    st.subheader("🔬 Column Profiling")
    
    profiling_df = create_data_profiling_summary(datasets)
    
    # Filters for profiling
    col1, col2 = st.columns(2)
    
    with col1:
        selected_datasets = st.multiselect(
            "Select Datasets",
            options=profiling_df['dataset'].unique(),
            default=profiling_df['dataset'].unique()
        )
    
    with col2:
        null_threshold = st.slider(
            "Show columns with null % >",
            min_value=0,
            max_value=50,
            value=0
        )
    
    # Apply filters
    filtered_profiling = profiling_df[
        (profiling_df['dataset'].isin(selected_datasets)) &
        (profiling_df['null_percentage'] > null_threshold)
    ].sort_values(['dataset', 'null_percentage'], ascending=[True, False])
    
    # Display profiling table
    st.dataframe(
        filtered_profiling,
        column_config={
            "null_percentage": st.column_config.NumberColumn(
                "Null %",
                format="%.1f%%"
            ),
            "unique_percentage": st.column_config.NumberColumn(
                "Unique %",
                format="%.1f%%"
            )
        },
        use_container_width=True
    )
    
    # Data quality alerts
    st.subheader("🚨 Data Quality Alerts")
    
    alerts = []
    
    for name, report in quality_report.items():
        # Check completeness
        if report['completeness_score'] < 90:
            alerts.append({
                'Level': '🔴 Critical',
                'Dataset': name,
                'Issue': 'Low completeness',
                'Details': f"Only {report['completeness_score']:.1f}% complete"
            })
        elif report['completeness_score'] < 95:
            alerts.append({
                'Level': '🟡 Warning',
                'Dataset': name,
                'Issue': 'Moderate completeness',
                'Details': f"{report['completeness_score']:.1f}% complete"
            })
        
        # Check duplicates
        if report['duplicate_percentage'] > 5:
            alerts.append({
                'Level': '🟡 Warning',
                'Dataset': name,
                'Issue': 'High duplicate rate',
                'Details': f"{report['duplicate_percentage']:.1f}% duplicates"
            })
        
        # Check for columns with high null rates
        for col, null_pct in report['null_percentages'].items():
            if null_pct > 20:
                alerts.append({
                    'Level': '🟡 Warning',
                    'Dataset': name,
                    'Issue': f'High nulls in {col}',
                    'Details': f"{null_pct:.1f}% missing values"
                })
    
    if alerts:
        alerts_df = pd.DataFrame(alerts)
        st.dataframe(alerts_df, use_container_width=True)
    else:
        st.success("✅ No data quality issues detected!")
    
    # Export functionality
    st.subheader("📤 Export Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Quality Report"):
            quality_export = pd.DataFrame([
                {
                    'dataset': name,
                    **report
                }
                for name, report in quality_report.items()
            ])
            csv = quality_export.to_csv(index=False)
            st.download_button(
                "Download Quality Report CSV",
                csv,
                f"data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("📋 Export Column Profiling"):
            csv = profiling_df.to_csv(index=False)
            st.download_button(
                "Download Profiling CSV",
                csv,
                f"column_profiling_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv"
            )

if __name__ == "__main__":
    main()