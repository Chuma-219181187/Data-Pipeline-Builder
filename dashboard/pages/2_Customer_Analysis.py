"""
Customer Analysis Page
Deep dive into customer behavior and segmentation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Customer Analysis",
    page_icon="👥",
    layout="wide"
)

def load_data():
    """Load data from session state or redirect to main page"""
    if 'datasets' not in st.session_state:
        st.warning("Please load data from the main dashboard first.")
        st.stop()
    return st.session_state['datasets']

def create_customer_segmentation(datasets):
    """Create RFM customer segmentation"""
    customers = datasets['customers']
    orders = datasets['orders']
    order_items = datasets['order_items']
    
    # Merge data
    customer_orders = customers.merge(orders, on='customer_id', how='inner')
    order_data = customer_orders.merge(order_items, on='order_id', how='inner')
    
    # Convert timestamp
    order_data['order_purchase_timestamp'] = pd.to_datetime(order_data['order_purchase_timestamp'])
    
    # Calculate RFM metrics
    current_date = order_data['order_purchase_timestamp'].max()
    
    rfm = order_data.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (current_date - x.max()).days,  # Recency
        'order_id': 'nunique',  # Frequency
        'price': 'sum'  # Monetary
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Add customer info
    rfm = rfm.merge(customers[['customer_id', 'customer_state', 'customer_city']], 
                    on='customer_id', how='left')
    
    # Create RFM scores
    rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5,4,3,2,1])
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
    
    # Combine scores
    rfm['rfm_score'] = rfm['r_score'].astype(str) + rfm['f_score'].astype(str) + rfm['m_score'].astype(str)
    
    # Create segments
    def segment_customers(row):
        if row['rfm_score'] in ['555', '554', '544', '545', '454', '455', '445']:
            return 'Champions'
        elif row['rfm_score'] in ['543', '444', '435', '355', '354', '345', '344', '335']:
            return 'Loyal Customers'
        elif row['rfm_score'] in ['553', '551', '552', '541', '542', '533', '532', '531', '452', '451']:
            return 'Potential Loyalists'
        elif row['rfm_score'] in ['512', '511', '422', '421', '412', '411', '311']:
            return 'New Customers'
        elif row['rfm_score'] in ['155', '154', '144', '214', '215', '115', '114']:
            return 'Cannot Lose Them'
        elif row['rfm_score'] in ['155', '254', '245']:
            return 'At Risk'
        elif row['rfm_score'] in ['233', '234', '343', '334', '343', '444']:
            return 'Need Attention'
        else:
            return 'Others'
    
    rfm['segment'] = rfm.apply(segment_customers, axis=1)
    
    return rfm

def create_geographic_analysis(datasets):
    """Analyze customer distribution by geography"""
    customers = datasets['customers']
    orders = datasets['orders']
    order_items = datasets['order_items']
    
    # Merge data
    customer_orders = customers.merge(orders, on='customer_id', how='inner')
    order_data = customer_orders.merge(order_items, on='order_id', how='inner')
    
    # State analysis
    state_analysis = order_data.groupby(['customer_state', 'customer_city']).agg({
        'customer_id': 'nunique',
        'order_id': 'nunique',
        'price': 'sum',
        'freight_value': 'sum'
    }).reset_index()
    
    state_analysis['total_revenue'] = state_analysis['price'] + state_analysis['freight_value']
    state_analysis['avg_order_value'] = state_analysis['total_revenue'] / state_analysis['order_id']
    
    return state_analysis

def main():
    st.title("👥 Customer Analysis")
    
    datasets = load_data()
    
    # Customer segmentation
    st.subheader("🎯 Customer Segmentation (RFM Analysis)")
    
    with st.spinner("Calculating RFM segmentation..."):
        rfm_data = create_customer_segmentation(datasets)
    
    # Display segment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        segment_counts = rfm_data['segment'].value_counts()
        fig_segments = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title='Customer Segment Distribution'
        )
        st.plotly_chart(fig_segments, use_container_width=True)
    
    with col2:
        # Segment value
        segment_value = rfm_data.groupby('segment')['monetary'].sum().reset_index()
        fig_value = px.bar(
            segment_value.sort_values('monetary', ascending=True),
            x='monetary',
            y='segment',
            orientation='h',
            title='Total Value by Customer Segment',
            labels={'monetary': 'Total Revenue ($)', 'segment': 'Customer Segment'}
        )
        st.plotly_chart(fig_value, use_container_width=True)
    
    # RFM scatter plot
    st.subheader("📊 RFM Analysis Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_rfm = px.scatter(
            rfm_data,
            x='recency',
            y='frequency',
            size='monetary',
            color='segment',
            title='Customer RFM Analysis',
            labels={'recency': 'Recency (Days)', 'frequency': 'Frequency (Orders)'},
            hover_data=['customer_state']
        )
        st.plotly_chart(fig_rfm, use_container_width=True)
    
    with col2:
        # Monetary vs Frequency
        fig_mf = px.scatter(
            rfm_data,
            x='frequency',
            y='monetary',
            color='segment',
            title='Frequency vs Monetary Value',
            labels={'frequency': 'Frequency (Orders)', 'monetary': 'Monetary Value ($)'}
        )
        st.plotly_chart(fig_mf, use_container_width=True)
    
    # Geographic analysis
    st.subheader("🗺️ Geographic Customer Distribution")
    
    geo_data = create_geographic_analysis(datasets)
    
    # State-level analysis
    state_summary = geo_data.groupby('customer_state').agg({
        'customer_id': 'sum',
        'order_id': 'sum',
        'total_revenue': 'sum',
        'avg_order_value': 'mean'
    }).reset_index().sort_values('total_revenue', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_state_customers = px.bar(
            state_summary.head(10),
            x='customer_state',
            y='customer_id',
            title='Top 10 States by Number of Customers',
            labels={'customer_id': 'Number of Customers', 'customer_state': 'State'}
        )
        st.plotly_chart(fig_state_customers, use_container_width=True)
    
    with col2:
        fig_state_revenue = px.bar(
            state_summary.head(10),
            x='customer_state',
            y='total_revenue',
            title='Top 10 States by Revenue',
            labels={'total_revenue': 'Total Revenue ($)', 'customer_state': 'State'}
        )
        st.plotly_chart(fig_state_revenue, use_container_width=True)
    
    # Customer lifetime value analysis
    st.subheader("💰 Customer Lifetime Value Analysis")
    
    # CLV histogram
    fig_clv = px.histogram(
        rfm_data,
        x='monetary',
        nbins=30,
        title='Customer Lifetime Value Distribution',
        labels={'monetary': 'Customer Lifetime Value ($)', 'count': 'Number of Customers'}
    )
    fig_clv.add_vline(
        x=rfm_data['monetary'].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text="Average CLV"
    )
    st.plotly_chart(fig_clv, use_container_width=True)
    
    # CLV metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_clv = rfm_data['monetary'].mean()
        st.metric("Average CLV", f"${avg_clv:.2f}")
    
    with col2:
        median_clv = rfm_data['monetary'].median()
        st.metric("Median CLV", f"${median_clv:.2f}")
    
    with col3:
        top_10_percent = rfm_data['monetary'].quantile(0.9)
        st.metric("Top 10% CLV", f"${top_10_percent:.2f}")
    
    with col4:
        total_customers = len(rfm_data)
        st.metric("Total Customers", f"{total_customers:,}")
    
    # Detailed customer table
    st.subheader("📋 Customer Details")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_segments = st.multiselect(
            "Filter by Segment",
            options=rfm_data['segment'].unique(),
            default=rfm_data['segment'].unique()
        )
    
    with col2:
        min_clv = st.number_input("Minimum CLV", min_value=0.0, value=0.0)
    
    with col3:
        selected_states = st.multiselect(
            "Filter by State",
            options=rfm_data['customer_state'].unique(),
            default=rfm_data['customer_state'].unique()[:5]  # Default to top 5 states
        )
    
    # Apply filters
    filtered_customers = rfm_data[
        (rfm_data['segment'].isin(selected_segments)) &
        (rfm_data['monetary'] >= min_clv) &
        (rfm_data['customer_state'].isin(selected_states))
    ].sort_values('monetary', ascending=False)
    
    # Display table
    st.dataframe(
        filtered_customers,
        column_config={
            "monetary": st.column_config.NumberColumn(
                "CLV",
                format="$%.2f"
            ),
            "recency": st.column_config.NumberColumn(
                "Recency (Days)",
                format="%d days"
            ),
            "frequency": st.column_config.NumberColumn(
                "Frequency (Orders)"
            )
        },
        use_container_width=True
    )
    
    # Customer insights
    st.subheader("🔍 Customer Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top Customer Segments by Value:**")
        top_segments = rfm_data.groupby('segment')['monetary'].agg(['count', 'mean', 'sum']).round(2)
        top_segments.columns = ['Count', 'Avg CLV', 'Total Value']
        top_segments = top_segments.sort_values('Total Value', ascending=False)
        st.dataframe(top_segments)
    
    with col2:
        st.write("**State Performance Summary:**")
        state_perf = rfm_data.groupby('customer_state')['monetary'].agg(['count', 'mean']).round(2)
        state_perf.columns = ['Customers', 'Avg CLV']
        state_perf = state_perf.sort_values('Avg CLV', ascending=False).head(10)
        st.dataframe(state_perf)

if __name__ == "__main__":
    main()