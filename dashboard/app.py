"""
E-Commerce Analytics Dashboard
Interactive Streamlit dashboard for Brazilian E-commerce data analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project directories to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

# Import with error handling
try:
    from src.etl.extract import DataExtractor
    from src.utils.logger import get_logger
except ImportError:
    # Fallback: create mock functions for demo mode
    class DataExtractor:
        def __init__(self):
            pass
        def generate_sample_data(self):
            return self._create_sample_data()
        def _create_sample_data(self):
            # Generate sample e-commerce data with correct column names
            np.random.seed(42)
            dates = pd.date_range('2023-01-01', periods=1000, freq='D')
            
            # Create orders data
            orders_data = {
                'order_id': [f'order_{i}' for i in range(1, 1001)],
                'customer_id': [f'customer_{i}' for i in np.random.randint(1, 500, 1000)],
                'order_purchase_timestamp': np.random.choice(dates, 1000),
                'order_status': np.random.choice(['delivered', 'shipped', 'processing'], 1000, p=[0.7, 0.2, 0.1])
            }
            
            # Create customers data
            customers_data = {
                'customer_id': [f'customer_{i}' for i in range(1, 501)],
                'customer_state': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'DF'], 500),
                'customer_city': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre'], 500)
            }
            
            # Create order items data
            order_items_data = {
                'order_id': [f'order_{i}' for i in range(1, 1001)],
                'product_id': [f'product_{i}' for i in np.random.randint(1, 200, 1000)],
                'price': np.random.normal(150, 50, 1000).clip(10, 1000),
                'freight_value': np.random.normal(20, 5, 1000).clip(5, 50)
            }
            
            # Create products data
            products_data = {
                'product_id': [f'product_{i}' for i in range(1, 201)],
                'product_category_name': np.random.choice([
                    'Electronics', 'Fashion', 'Home & Garden', 'Sports', 'Books', 'Beauty', 'Health'
                ], 200)
            }
            
            return {
                'orders': pd.DataFrame(orders_data),
                'customers': pd.DataFrame(customers_data),
                'order_items': pd.DataFrame(order_items_data), 
                'products': pd.DataFrame(products_data),
                'reviews': pd.DataFrame()  # Empty reviews for simplicity
            }
            return pd.DataFrame(data)
    
    def get_logger(name):
        import logging
        return logging.getLogger(name)

# Configure page
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = get_logger(__name__)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the dataset"""
    try:
        extractor = DataExtractor()
        
        # Try to load real data, fallback to sample data
        try:
            datasets = extractor.extract_data()
            if datasets is None:
                raise Exception("No data returned from extractor")
        except:
            # Use sample data if real data extraction fails
            datasets = extractor.generate_sample_data()
        
        # Store in session state for other pages
        st.session_state['datasets'] = datasets
        
        return datasets
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        # Return minimal sample data as last resort with correct column names
        orders_data = pd.DataFrame({
            'order_id': [f'order_{i}' for i in range(1, 101)],
            'customer_id': [f'customer_{i}' for i in np.random.randint(1, 50, 100)],
            'order_purchase_timestamp': pd.date_range('2023-01-01', periods=100, freq='D'),
            'order_status': np.random.choice(['delivered', 'shipped'], 100)
        })
        
        customers_data = pd.DataFrame({
            'customer_id': [f'customer_{i}' for i in range(1, 51)],
            'customer_state': np.random.choice(['SP', 'RJ', 'MG'], 50)
        })
        
        order_items_data = pd.DataFrame({
            'order_id': [f'order_{i}' for i in range(1, 101)],
            'product_id': [f'product_{i}' for i in np.random.randint(1, 20, 100)],
            'price': np.random.normal(150, 50, 100).clip(10, 500)
        })
        
        return {
            'orders': orders_data,
            'customers': customers_data,
            'order_items': order_items_data,
            'products': pd.DataFrame({'product_id': [f'product_{i}' for i in range(1, 21)], 
                                    'product_category_name': np.random.choice(['Electronics', 'Fashion'], 20)}),
            'reviews': pd.DataFrame()
        }

def calculate_kpis(datasets):
    """Calculate key performance indicators"""
    try:
        orders = datasets['orders']
        order_items = datasets['order_items']
        customers = datasets['customers']
        reviews = datasets.get('reviews', pd.DataFrame())
        
        # Merge orders with order_items for calculations
        order_data = orders.merge(order_items, on='order_id', how='inner')
        
        # Calculate KPIs
        total_revenue = order_data['price'].sum() + order_data['freight_value'].sum()
        total_orders = len(orders)
        total_customers = len(customers)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Calculate delivery performance
        delivered_orders = orders[orders['order_status'] == 'delivered']
        delivery_rate = (len(delivered_orders) / total_orders * 100) if total_orders > 0 else 0
        
        # Calculate average review score
        avg_review_score = reviews['review_score'].mean() if not reviews.empty else 0
        
        return {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'total_customers': total_customers,
            'avg_order_value': avg_order_value,
            'delivery_rate': delivery_rate,
            'avg_review_score': avg_review_score
        }
    
    except Exception as e:
        st.error(f"Error calculating KPIs: {str(e)}")
        return {}

def create_revenue_chart(datasets):
    """Create revenue trend chart"""
    try:
        orders = datasets['orders']
        order_items = datasets['order_items']
        
        # Merge and calculate daily revenue
        order_data = orders.merge(order_items, on='order_id', how='inner')
        order_data['order_purchase_timestamp'] = pd.to_datetime(order_data['order_purchase_timestamp'])
        order_data['total_amount'] = order_data['price'] + order_data['freight_value']
        
        # Group by date
        daily_revenue = order_data.groupby(
            order_data['order_purchase_timestamp'].dt.date
        )['total_amount'].sum().reset_index()
        
        fig = px.line(
            daily_revenue,
            x='order_purchase_timestamp',
            y='total_amount',
            title='Daily Revenue Trend',
            labels={'total_amount': 'Revenue ($)', 'order_purchase_timestamp': 'Date'}
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            showlegend=False
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating revenue chart: {str(e)}")
        return None

def create_state_analysis(datasets):
    """Create state-wise sales analysis"""
    try:
        customers = datasets['customers']
        orders = datasets['orders']
        order_items = datasets['order_items']
        
        # Merge data
        customer_orders = customers.merge(orders, on='customer_id', how='inner')
        order_data = customer_orders.merge(order_items, on='order_id', how='inner')
        
        # Group by state
        state_data = order_data.groupby('customer_state').agg({
            'order_id': 'nunique',
            'price': 'sum',
            'freight_value': 'sum',
            'customer_id': 'nunique'
        }).reset_index()
        
        state_data['total_revenue'] = state_data['price'] + state_data['freight_value']
        state_data = state_data.sort_values('total_revenue', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            state_data.head(10),
            x='customer_state',
            y='total_revenue',
            title='Top 10 States by Revenue',
            labels={'total_revenue': 'Revenue ($)', 'customer_state': 'State'},
            color='total_revenue',
            color_continuous_scale='Blues'
        )
        
        return fig, state_data
    
    except Exception as e:
        st.error(f"Error creating state analysis: {str(e)}")
        return None, None

def create_product_category_chart(datasets):
    """Create product category performance chart"""
    try:
        products = datasets['products']
        order_items = datasets['order_items']
        
        # Merge data
        product_sales = products.merge(order_items, on='product_id', how='inner')
        
        # Group by category
        category_data = product_sales.groupby('product_category_name').agg({
            'price': ['sum', 'count', 'mean']
        }).reset_index()
        
        category_data.columns = ['category', 'total_revenue', 'items_sold', 'avg_price']
        category_data = category_data.sort_values('total_revenue', ascending=False)
        
        # Create pie chart for top categories
        fig = px.pie(
            category_data.head(8),
            values='total_revenue',
            names='category',
            title='Revenue Distribution by Product Category (Top 8)'
        )
        
        return fig, category_data
    
    except Exception as e:
        st.error(f"Error creating category chart: {str(e)}")
        return None, None

def create_order_status_chart(datasets):
    """Create order status distribution chart"""
    try:
        orders = datasets['orders']
        
        status_counts = orders['order_status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title='Order Status Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating order status chart: {str(e)}")
        return None

def create_customer_metrics_chart(datasets):
    """Create customer behavior metrics"""
    try:
        customers = datasets['customers']
        orders = datasets['orders']
        order_items = datasets['order_items']
        
        # Calculate customer metrics
        customer_orders = customers.merge(orders, on='customer_id', how='left')
        order_data = customer_orders.merge(order_items, on='order_id', how='left')
        
        customer_metrics = order_data.groupby('customer_id').agg({
            'order_id': 'nunique',
            'price': 'sum',
            'freight_value': 'sum'
        }).fillna(0)
        
        customer_metrics['total_spent'] = customer_metrics['price'] + customer_metrics['freight_value']
        customer_metrics = customer_metrics[customer_metrics['order_id'] > 0]  # Remove customers with no orders
        
        # Create histogram of customer spending
        fig = px.histogram(
            customer_metrics,
            x='total_spent',
            nbins=30,
            title='Customer Spending Distribution',
            labels={'total_spent': 'Total Amount Spent ($)', 'count': 'Number of Customers'}
        )
        
        return fig, customer_metrics
    
    except Exception as e:
        st.error(f"Error creating customer metrics: {str(e)}")
        return None, None

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        datasets = load_data()
    
    if datasets is None:
        st.stop()
    
    # Sidebar filters
    st.sidebar.markdown('<p class="sidebar-header">🔧 Filters & Controls</p>', unsafe_allow_html=True)
    
    # Date range filter
    if 'orders' in datasets:
        orders = datasets['orders']
        orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
        
        min_date = orders['order_purchase_timestamp'].min().date()
        max_date = orders['order_purchase_timestamp'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Filter data by date range
        if len(date_range) == 2:
            start_date, end_date = date_range
            mask = (orders['order_purchase_timestamp'].dt.date >= start_date) & \
                   (orders['order_purchase_timestamp'].dt.date <= end_date)
            filtered_orders = orders[mask]
            datasets['orders'] = filtered_orders
    
    # Order status filter
    if 'orders' in datasets:
        status_options = ['All'] + list(datasets['orders']['order_status'].unique())
        selected_status = st.sidebar.selectbox("Filter by Order Status", status_options)
        
        if selected_status != 'All':
            datasets['orders'] = datasets['orders'][datasets['orders']['order_status'] == selected_status]
    
    # Calculate KPIs
    kpis = calculate_kpis(datasets)
    
    # Display KPIs
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"${kpis.get('total_revenue', 0):,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📦 Total Orders",
            value=f"{kpis.get('total_orders', 0):,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="👥 Total Customers",
            value=f"{kpis.get('total_customers', 0):,}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="💵 Avg Order Value",
            value=f"${kpis.get('avg_order_value', 0):.2f}",
            delta=None
        )
    
    # Additional KPIs
    col5, col6 = st.columns(2)
    
    with col5:
        st.metric(
            label="🚚 Delivery Rate",
            value=f"{kpis.get('delivery_rate', 0):.1f}%",
            delta=None
        )
    
    with col6:
        st.metric(
            label="⭐ Avg Review Score",
            value=f"{kpis.get('avg_review_score', 0):.2f}/5.0",
            delta=None
        )
    
    st.divider()
    
    # Charts section
    st.subheader("📊 Analytics & Insights")
    
    # Revenue trend
    col1, col2 = st.columns(2)
    
    with col1:
        revenue_chart = create_revenue_chart(datasets)
        if revenue_chart:
            st.plotly_chart(revenue_chart, use_container_width=True)
    
    with col2:
        order_status_chart = create_order_status_chart(datasets)
        if order_status_chart:
            st.plotly_chart(order_status_chart, use_container_width=True)
    
    # State and category analysis
    col3, col4 = st.columns(2)
    
    with col3:
        state_chart, state_data = create_state_analysis(datasets)
        if state_chart:
            st.plotly_chart(state_chart, use_container_width=True)
    
    with col4:
        category_chart, category_data = create_product_category_chart(datasets)
        if category_chart:
            st.plotly_chart(category_chart, use_container_width=True)
    
    # Customer analysis
    st.subheader("👥 Customer Analysis")
    
    customer_chart, customer_data = create_customer_metrics_chart(datasets)
    if customer_chart:
        st.plotly_chart(customer_chart, use_container_width=True)
    
    # Data tables section
    st.subheader("📋 Data Tables")
    
    # Expandable data views
    with st.expander("🏆 Top Performing States"):
        if state_data is not None:
            st.dataframe(state_data.head(10), use_container_width=True)
    
    with st.expander("🛍️ Product Category Performance"):
        if category_data is not None:
            st.dataframe(category_data.head(10), use_container_width=True)
    
    with st.expander("👑 Top Customers by Spending"):
        if customer_data is not None:
            top_customers = customer_data.sort_values('total_spent', ascending=False).head(20)
            st.dataframe(top_customers, use_container_width=True)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #888888; padding: 1rem;'>
        📊 E-Commerce Analytics Dashboard | Built with Streamlit & Plotly<br>
        Data Pipeline Project - Week 4 | Powered by Brazilian E-commerce Dataset
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()