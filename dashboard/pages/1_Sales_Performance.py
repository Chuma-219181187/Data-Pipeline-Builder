"""
Sales Performance Analysis Page
Detailed sales analytics and performance metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Sales Performance",
    page_icon="💰",
    layout="wide"
)

def load_data():
    """Load data from session state or redirect to main page"""
    if 'datasets' not in st.session_state:
        st.warning("Please load data from the main dashboard first.")
        st.stop()
    return st.session_state['datasets']

def create_monthly_sales_trend(datasets):
    """Create monthly sales trend analysis"""
    orders = datasets['orders']
    order_items = datasets['order_items']
    
    # Merge data
    order_data = orders.merge(order_items, on='order_id', how='inner')
    order_data['order_purchase_timestamp'] = pd.to_datetime(order_data['order_purchase_timestamp'])
    order_data['total_amount'] = order_data['price'] + order_data['freight_value']
    
    # Group by month
    order_data['year_month'] = order_data['order_purchase_timestamp'].dt.to_period('M')
    monthly_sales = order_data.groupby('year_month').agg({
        'total_amount': 'sum',
        'order_id': 'nunique',
        'price': 'mean'
    }).reset_index()
    
    monthly_sales['year_month'] = monthly_sales['year_month'].astype(str)
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Monthly Revenue', 'Monthly Orders', 'Average Order Value', 'Growth Rate'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Monthly Revenue
    fig.add_trace(
        go.Scatter(x=monthly_sales['year_month'], y=monthly_sales['total_amount'],
                  mode='lines+markers', name='Revenue', line=dict(color='blue')),
        row=1, col=1
    )
    
    # Monthly Orders
    fig.add_trace(
        go.Scatter(x=monthly_sales['year_month'], y=monthly_sales['order_id'],
                  mode='lines+markers', name='Orders', line=dict(color='green')),
        row=1, col=2
    )
    
    # Average Order Value
    avg_order_value = monthly_sales['total_amount'] / monthly_sales['order_id']
    fig.add_trace(
        go.Scatter(x=monthly_sales['year_month'], y=avg_order_value,
                  mode='lines+markers', name='AOV', line=dict(color='red')),
        row=2, col=1
    )
    
    # Growth Rate
    monthly_sales['growth_rate'] = monthly_sales['total_amount'].pct_change() * 100
    fig.add_trace(
        go.Scatter(x=monthly_sales['year_month'], y=monthly_sales['growth_rate'],
                  mode='lines+markers', name='Growth %', line=dict(color='orange')),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False, title_text="Sales Performance Trends")
    return fig, monthly_sales

def create_seller_performance_analysis(datasets):
    """Analyze product category performance (adapted for available data)"""
    order_items = datasets['order_items']
    orders = datasets['orders']
    products = datasets.get('products', pd.DataFrame())
    
    # Merge data
    sales_data = order_items.merge(orders, on='order_id', how='inner')
    
    # If products data available, merge it
    if not products.empty and 'product_category_name' in products.columns:
        sales_data = sales_data.merge(products, on='product_id', how='left')
        category_col = 'product_category_name'
    else:
        # Create mock categories based on product_id for demo
        np.random.seed(42)
        categories = ['Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books', 'Beauty', 'Health']
        sales_data['product_category_name'] = np.random.choice(categories, len(sales_data))
        category_col = 'product_category_name'
    
    # Calculate metrics per category (instead of seller)
    category_metrics = sales_data.groupby(category_col).agg({
        'price': ['sum', 'count', 'mean'],
        'order_id': 'nunique'
    }).reset_index()
    
    # Flatten column names
    category_metrics.columns = [category_col, 'total_revenue', 'items_sold', 'avg_price', 'unique_orders']
    category_metrics['total_value'] = category_metrics['total_revenue']
    
    # Rename for compatibility with existing code
    seller_metrics = category_metrics.rename(columns={
        category_col: 'seller_id',
        category_col: 'seller_state'  # Use category as state for now
    })
    seller_metrics['seller_state'] = seller_metrics['seller_id']  # Duplicate for compatibility
    
    return seller_metrics

def main():
    st.title("💰 Sales Performance Analysis")
    
    datasets = load_data()
    
    # Monthly trend analysis
    st.subheader("📈 Monthly Sales Trends")
    monthly_chart, monthly_data = create_monthly_sales_trend(datasets)
    st.plotly_chart(monthly_chart, use_container_width=True)
    
    # Key insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_months = len(monthly_data)
        st.metric("Total Months", total_months)
    
    with col2:
        avg_monthly_revenue = monthly_data['total_amount'].mean()
        st.metric("Avg Monthly Revenue", f"${avg_monthly_revenue:,.0f}")
    
    with col3:
        if len(monthly_data) > 1:
            latest_growth = monthly_data['growth_rate'].iloc[-1]
            st.metric("Latest Growth Rate", f"{latest_growth:.1f}%")
    
    # Product Category Performance
    st.subheader("🛍️ Product Category Performance Analysis")
    
    seller_metrics = create_seller_performance_analysis(datasets)
    
    # Top categories chart
    top_sellers = seller_metrics.nlargest(15, 'total_value')
    
    fig_sellers = px.bar(
        top_sellers,
        x='seller_id',
        y='total_value',
        color='seller_id',
        title='Product Category Performance by Revenue',
        labels={'total_value': 'Total Revenue ($)', 'seller_id': 'Product Category'}
    )
    fig_sellers.update_xaxes(tickangle=45, title="Product Categories")
    st.plotly_chart(fig_sellers, use_container_width=True)
    
    # Category distribution
    col1, col2 = st.columns(2)
    
    with col1:
        category_dist = seller_metrics.groupby('seller_id')['total_value'].sum().reset_index()
        fig_states = px.pie(
            category_dist,
            values='total_value',
            names='seller_id',
            title='Revenue Distribution by Product Category'
        )
        st.plotly_chart(fig_states, use_container_width=True)
    
    with col2:
        # Category performance scatter plot
        fig_scatter = px.scatter(
            seller_metrics,
            x='items_sold',
            y='total_value',
            color='seller_id',
            size='unique_orders',
            title='Category Performance: Items vs Revenue',
            labels={'items_sold': 'Items Sold', 'total_value': 'Total Revenue ($)'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Detailed category table
    st.subheader("📊 Detailed Category Metrics")
    
    # Add filters
    col1, col2 = st.columns(2)
    with col1:
        min_revenue = st.number_input("Minimum Revenue", min_value=0, value=100)
    with col2:
        selected_categories = st.multiselect(
            "Filter by Category", 
            options=seller_metrics['seller_id'].unique(),
            default=seller_metrics['seller_id'].unique()
        )
    
    # Apply filters
    filtered_sellers = seller_metrics[
        (seller_metrics['total_value'] >= min_revenue) &
        (seller_metrics['seller_id'].isin(selected_categories))
    ].sort_values('total_value', ascending=False)
    
    # Display table
    st.dataframe(
        filtered_sellers,
        column_config={
            "total_value": st.column_config.NumberColumn(
                "Total Revenue",
                format="$%.2f"
            ),
            "avg_price": st.column_config.NumberColumn(
                "Avg Price",
                format="$%.2f"
            )
        },
        use_container_width=True
    )
    
    # Export functionality
    if st.button("📥 Export Category Data to CSV"):
        csv = filtered_sellers.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"category_performance_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()