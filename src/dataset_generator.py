"""
Dataset Downloader and Analyzer
Downloads sample data and analyzes structure for ETL pipeline design
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime, timedelta
import random

# Set up paths
DATA_DIR = Path(__file__).parent.parent / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SAMPLE_DATA_DIR = DATA_DIR / "sample"

# Create directories
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

def generate_sample_ecommerce_data():
    """
    Generate sample e-commerce data for demonstration
    This creates a realistic dataset structure similar to the Brazilian e-commerce dataset
    """
    
    print("Generating sample e-commerce dataset...")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Generate Customers
    num_customers = 5000
    customers = pd.DataFrame({
        'customer_id': [f'CUST_{i:06d}' for i in range(1, num_customers + 1)],
        'customer_city': np.random.choice([
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 
            'Brasília', 'Fortaleza', 'Curitiba', 'Recife', 'Porto Alegre', 'Manaus'
        ], num_customers),
        'customer_state': np.random.choice([
            'SP', 'RJ', 'MG', 'BA', 'DF', 'CE', 'PR', 'PE', 'RS', 'AM'
        ], num_customers),
        'customer_zip_code_prefix': np.random.randint(10000, 99999, num_customers)
    })
    
    # Generate Products
    num_products = 1000
    product_categories = [
        'Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 
        'Beauty', 'Automotive', 'Toys', 'Health', 'Music'
    ]
    
    products = pd.DataFrame({
        'product_id': [f'PROD_{i:06d}' for i in range(1, num_products + 1)],
        'product_category_name': np.random.choice(product_categories, num_products),
        'product_name_length': np.random.randint(20, 80, num_products),
        'product_description_length': np.random.randint(100, 500, num_products),
        'product_weight_g': np.random.randint(50, 5000, num_products),
        'product_length_cm': np.random.randint(5, 50, num_products),
        'product_height_cm': np.random.randint(2, 30, num_products),
        'product_width_cm': np.random.randint(5, 40, num_products)
    })
    
    # Generate Sellers
    num_sellers = 500
    sellers = pd.DataFrame({
        'seller_id': [f'SELL_{i:06d}' for i in range(1, num_sellers + 1)],
        'seller_city': np.random.choice([
            'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 
            'Brasília', 'Fortaleza', 'Curitiba', 'Recife', 'Porto Alegre', 'Manaus'
        ], num_sellers),
        'seller_state': np.random.choice([
            'SP', 'RJ', 'MG', 'BA', 'DF', 'CE', 'PR', 'PE', 'RS', 'AM'
        ], num_sellers),
        'seller_zip_code_prefix': np.random.randint(10000, 99999, num_sellers)
    })
    
    # Generate Orders
    num_orders = 10000
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    orders = []
    for i in range(1, num_orders + 1):
        order_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        # Add delivery time (1-30 days later)
        delivered_date = order_date + timedelta(days=random.randint(1, 30))
        
        orders.append({
            'order_id': f'ORD_{i:08d}',
            'customer_id': np.random.choice(customers['customer_id']),
            'order_status': np.random.choice([
                'delivered', 'shipped', 'processing', 'canceled'
            ], p=[0.7, 0.15, 0.1, 0.05]),
            'order_purchase_timestamp': order_date,
            'order_delivered_timestamp': delivered_date if random.random() > 0.2 else None,
            'order_estimated_delivery_date': order_date + timedelta(days=random.randint(5, 45))
        })
    
    orders_df = pd.DataFrame(orders)
    
    # Generate Order Items
    order_items = []
    for order_id in orders_df['order_id']:
        num_items = random.randint(1, 5)  # 1-5 items per order
        
        for item_seq in range(1, num_items + 1):
            product_id = np.random.choice(products['product_id'])
            base_price = random.uniform(10, 500)
            
            order_items.append({
                'order_id': order_id,
                'order_item_id': item_seq,
                'product_id': product_id,
                'seller_id': np.random.choice(sellers['seller_id']),
                'shipping_limit_date': orders_df[orders_df['order_id'] == order_id]['order_purchase_timestamp'].iloc[0] + timedelta(days=random.randint(1, 7)),
                'price': round(base_price, 2),
                'freight_value': round(base_price * random.uniform(0.05, 0.2), 2)
            })
    
    order_items_df = pd.DataFrame(order_items)
    
    # Generate Order Reviews
    reviews = []
    delivered_orders = orders_df[orders_df['order_status'] == 'delivered']['order_id']
    
    for order_id in delivered_orders.sample(n=int(len(delivered_orders) * 0.8)):  # 80% review rate
        reviews.append({
            'review_id': f'REV_{len(reviews) + 1:08d}',
            'order_id': order_id,
            'review_score': np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.1, 0.15, 0.3, 0.4]),
            'review_comment_title': f'Review for order {order_id}',
            'review_comment_message': f'Customer feedback for order {order_id}',
            'review_creation_date': orders_df[orders_df['order_id'] == order_id]['order_delivered_timestamp'].iloc[0] + timedelta(days=random.randint(0, 10)),
            'review_answer_timestamp': None
        })
    
    reviews_df = pd.DataFrame(reviews)
    
    # Save datasets
    datasets = {
        'olist_customers_dataset.csv': customers,
        'olist_products_dataset.csv': products,
        'olist_sellers_dataset.csv': sellers,
        'olist_orders_dataset.csv': orders_df,
        'olist_order_items_dataset.csv': order_items_df,
        'olist_order_reviews_dataset.csv': reviews_df
    }
    
    for filename, df in datasets.items():
        filepath = SAMPLE_DATA_DIR / filename
        df.to_csv(filepath, index=False)
        print(f"Saved {filename}: {len(df)} records")
    
    return datasets

def analyze_dataset_structure(datasets):
    """Analyze the structure of the dataset for ETL design"""
    
    print("\n" + "="*50)
    print("DATASET STRUCTURE ANALYSIS")
    print("="*50)
    
    for filename, df in datasets.items():
        table_name = filename.replace('olist_', '').replace('_dataset.csv', '')
        print(f"\n📊 Table: {table_name.upper()}")
        print(f"   Rows: {len(df):,}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Memory: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        print("   Schema:")
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            print(f"     - {col}: {dtype} (null: {null_count}/{null_pct:.1f}%)")
    
    # Relationship Analysis
    print(f"\n🔗 RELATIONSHIP ANALYSIS")
    print("-" * 30)
    
    relationships = [
        ("customers", "customer_id", "orders", "customer_id"),
        ("orders", "order_id", "order_items", "order_id"),
        ("products", "product_id", "order_items", "product_id"),
        ("sellers", "seller_id", "order_items", "seller_id"),
        ("orders", "order_id", "order_reviews", "order_id")
    ]
    
    for parent_table, parent_key, child_table, child_key in relationships:
        print(f"   {parent_table}.{parent_key} → {child_table}.{child_key}")
    
    # Data Quality Analysis
    print(f"\n🔍 DATA QUALITY INSIGHTS")
    print("-" * 30)
    
    orders_df = datasets['olist_orders_dataset.csv']
    order_items_df = datasets['olist_order_items_dataset.csv']
    
    # Calculate some business metrics
    total_revenue = order_items_df['price'].sum()
    avg_order_value = order_items_df.groupby('order_id')['price'].sum().mean()
    total_orders = len(orders_df)
    
    print(f"   📈 Total Revenue: ${total_revenue:,.2f}")
    print(f"   📦 Total Orders: {total_orders:,}")
    print(f"   💰 Average Order Value: ${avg_order_value:.2f}")
    print(f"   📅 Date Range: {orders_df['order_purchase_timestamp'].min()} to {orders_df['order_purchase_timestamp'].max()}")
    
    return True

def main():
    """Main execution function"""
    print("🚀 Starting Dataset Generation and Analysis")
    print("=" * 50)
    
    # Generate sample data
    datasets = generate_sample_ecommerce_data()
    
    # Analyze structure
    analyze_dataset_structure(datasets)
    
    print(f"\n✅ Dataset generation complete!")
    print(f"📁 Files saved to: {SAMPLE_DATA_DIR}")
    print(f"\nNext steps:")
    print(f"1. Review the generated data structure")
    print(f"2. Design database schema based on relationships")
    print(f"3. Implement ETL pipeline components")

if __name__ == "__main__":
    main()