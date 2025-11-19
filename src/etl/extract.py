"""
Data Extraction Module
Handles data ingestion from multiple sources with error handling and validation
"""

import pandas as pd
import requests
import json
import os
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import time
import hashlib

from ..utils.logger import get_logger, log_execution_time

logger = get_logger(__name__)


class DataExtractor:
    """Extract data from various sources including CSV, JSON, APIs, and compressed files"""
    
    def __init__(self):
        """Initialize the DataExtractor with configuration"""
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.sample_data_dir = self.data_dir / "sample"
        
        # Create directories if they don't exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.sample_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.retry_attempts = int(os.getenv("RETRY_ATTEMPTS", 3))
        self.retry_delay = 2  # seconds
        
        logger.info("DataExtractor initialized")

    @log_execution_time
    def extract_data(self) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Main extraction method that coordinates data ingestion from all sources
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of extracted dataframes
        """
        try:
            logger.info("Starting data extraction process")
            
            # Try to extract from different sources in order of preference
            datasets = None
            
            # 1. Try to extract from Kaggle dataset (if downloaded)
            datasets = self.extract_from_kaggle()
            
            if datasets is None:
                # 2. Fall back to sample data
                logger.info("Kaggle data not found, generating sample data")
                datasets = self.extract_sample_data()
            
            if datasets is None:
                # 3. Fall back to API data (if available)
                logger.info("Sample data generation failed, trying API extraction")
                datasets = self.extract_from_api()
            
            if datasets is None:
                logger.error("All data extraction methods failed")
                return None
            
            # Validate extracted data
            validated_datasets = self.validate_extracted_data(datasets)
            
            logger.info(f"Successfully extracted {len(validated_datasets)} datasets")
            return validated_datasets
            
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            return None

    def extract_from_kaggle(self) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Extract data from downloaded Kaggle dataset files
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of dataframes from Kaggle files
        """
        try:
            logger.info("Attempting to extract Kaggle dataset")
            
            # Expected Kaggle files
            kaggle_files = {
                'customers': 'olist_customers_dataset.csv',
                'orders': 'olist_orders_dataset.csv',
                'order_items': 'olist_order_items_dataset.csv',
                'products': 'olist_products_dataset.csv',
                'sellers': 'olist_sellers_dataset.csv',
                'reviews': 'olist_order_reviews_dataset.csv'
            }
            
            datasets = {}
            missing_files = []
            
            for name, filename in kaggle_files.items():
                file_path = self.raw_data_dir / filename
                
                if file_path.exists():
                    try:
                        df = pd.read_csv(file_path, encoding='utf-8')
                        datasets[name] = df
                        logger.info(f"Loaded {name}: {len(df)} records from {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to load {filename}: {str(e)}")
                        missing_files.append(filename)
                else:
                    missing_files.append(filename)
            
            if missing_files:
                logger.warning(f"Missing Kaggle files: {missing_files}")
                return None
            
            return datasets
            
        except Exception as e:
            logger.warning(f"Kaggle extraction failed: {str(e)}")
            return None

    def extract_sample_data(self) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Generate and extract sample e-commerce data for demonstration
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of sample dataframes
        """
        try:
            logger.info("Generating sample e-commerce data")
            
            # Check if sample data already exists
            sample_files = list(self.sample_data_dir.glob("*.csv"))
            if sample_files:
                logger.info("Found existing sample data, loading...")
                return self._load_existing_sample_data()
            
            # Generate new sample data
            datasets = self._generate_sample_datasets()
            
            # Save sample data for future use
            self._save_sample_data(datasets)
            
            return datasets
            
        except Exception as e:
            logger.error(f"Sample data generation failed: {str(e)}")
            return None

    def extract_from_api(self) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Extract data from external APIs (placeholder for future implementation)
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of dataframes from API
        """
        try:
            logger.info("API extraction not implemented yet")
            return None
            
        except Exception as e:
            logger.error(f"API extraction failed: {str(e)}")
            return None

    def extract_from_url(self, url: str, file_type: str = 'csv') -> Optional[pd.DataFrame]:
        """
        Extract data from a URL with retry logic
        
        Args:
            url (str): URL to download data from
            file_type (str): Type of file (csv, json, excel)
        
        Returns:
            pd.DataFrame: Extracted dataframe
        """
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Downloading from URL (attempt {attempt + 1}): {url}")
                
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                if file_type.lower() == 'csv':
                    df = pd.read_csv(url)
                elif file_type.lower() == 'json':
                    df = pd.read_json(url)
                elif file_type.lower() in ['xlsx', 'excel']:
                    df = pd.read_excel(url)
                else:
                    raise ValueError(f"Unsupported file type: {file_type}")
                
                logger.info(f"Successfully downloaded {len(df)} records")
                return df
                
            except Exception as e:
                logger.warning(f"URL extraction attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All URL extraction attempts failed for {url}")
                    return None

    def extract_from_zip(self, zip_path: Union[str, Path]) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Extract multiple CSV files from a ZIP archive
        
        Args:
            zip_path (Union[str, Path]): Path to ZIP file
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of extracted dataframes
        """
        try:
            logger.info(f"Extracting from ZIP file: {zip_path}")
            
            datasets = {}
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # List all CSV files in the archive
                csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
                
                for csv_file in csv_files:
                    try:
                        # Extract and read CSV
                        with zip_ref.open(csv_file) as file:
                            df = pd.read_csv(file)
                            
                        # Use filename (without extension) as key
                        key = Path(csv_file).stem
                        datasets[key] = df
                        
                        logger.info(f"Extracted {key}: {len(df)} records")
                        
                    except Exception as e:
                        logger.warning(f"Failed to extract {csv_file}: {str(e)}")
            
            return datasets if datasets else None
            
        except Exception as e:
            logger.error(f"ZIP extraction failed: {str(e)}")
            return None

    def validate_extracted_data(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Validate extracted datasets for basic quality checks
        
        Args:
            datasets (Dict[str, pd.DataFrame]): Raw extracted datasets
        
        Returns:
            Dict[str, pd.DataFrame]: Validated datasets
        """
        try:
            logger.info("Validating extracted datasets")
            
            validated_datasets = {}
            validation_errors = []
            
            for name, df in datasets.items():
                try:
                    # Basic validation checks
                    if df is None or df.empty:
                        validation_errors.append(f"{name}: Dataset is empty")
                        continue
                    
                    if len(df.columns) < 2:
                        validation_errors.append(f"{name}: Dataset has too few columns ({len(df.columns)})")
                        continue
                    
                    # Check for minimum row count
                    min_rows = 10  # Minimum acceptable rows for processing
                    if len(df) < min_rows:
                        validation_errors.append(f"{name}: Dataset has too few rows ({len(df)})")
                        continue
                    
                    # Calculate basic statistics
                    total_cells = len(df) * len(df.columns)
                    null_cells = df.isnull().sum().sum()
                    null_percentage = (null_cells / total_cells) * 100
                    
                    logger.info(f"{name} validation - Rows: {len(df)}, Columns: {len(df.columns)}, Nulls: {null_percentage:.1f}%")
                    
                    # Add metadata to dataframe
                    df.attrs['extraction_timestamp'] = datetime.now()
                    df.attrs['source_name'] = name
                    df.attrs['null_percentage'] = null_percentage
                    
                    validated_datasets[name] = df
                    
                except Exception as e:
                    validation_errors.append(f"{name}: Validation error - {str(e)}")
            
            if validation_errors:
                logger.warning(f"Validation errors: {validation_errors}")
            
            logger.info(f"Validation complete. {len(validated_datasets)} datasets passed validation")
            return validated_datasets
            
        except Exception as e:
            logger.error(f"Dataset validation failed: {str(e)}")
            return datasets  # Return original datasets if validation fails

    def _generate_sample_datasets(self) -> Dict[str, pd.DataFrame]:
        """Generate sample e-commerce datasets"""
        import numpy as np
        import random
        from datetime import timedelta
        
        # Set seed for reproducibility
        np.random.seed(42)
        random.seed(42)
        
        # Generate Customers
        num_customers = 1000
        customers = pd.DataFrame({
            'customer_id': [f'CUST_{i:06d}' for i in range(1, num_customers + 1)],
            'customer_unique_id': [f'UNIQ_{i:06d}' for i in range(1, num_customers + 1)],
            'customer_zip_code_prefix': np.random.randint(10000, 99999, num_customers),
            'customer_city': np.random.choice([
                'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador', 
                'Brasília', 'Fortaleza', 'Curitiba'
            ], num_customers),
            'customer_state': np.random.choice(['SP', 'RJ', 'MG', 'BA', 'DF', 'CE', 'PR'], num_customers)
        })
        
        # Generate Products
        num_products = 500
        categories = ['Electronics', 'Fashion', 'Home', 'Sports', 'Books', 'Beauty', 'Health']
        products = pd.DataFrame({
            'product_id': [f'PROD_{i:06d}' for i in range(1, num_products + 1)],
            'product_category_name': np.random.choice(categories, num_products),
            'product_name_length': np.random.randint(20, 80, num_products),
            'product_description_length': np.random.randint(100, 500, num_products),
            'product_photos_qty': np.random.randint(1, 10, num_products),
            'product_weight_g': np.random.randint(50, 5000, num_products),
            'product_length_cm': np.random.randint(5, 50, num_products),
            'product_height_cm': np.random.randint(2, 30, num_products),
            'product_width_cm': np.random.randint(5, 40, num_products)
        })
        
        # Generate Sellers
        num_sellers = 200
        sellers = pd.DataFrame({
            'seller_id': [f'SELL_{i:06d}' for i in range(1, num_sellers + 1)],
            'seller_zip_code_prefix': np.random.randint(10000, 99999, num_sellers),
            'seller_city': np.random.choice([
                'São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador'
            ], num_sellers),
            'seller_state': np.random.choice(['SP', 'RJ', 'MG', 'BA'], num_sellers)
        })
        
        # Generate Orders
        num_orders = 2000
        start_date = datetime(2023, 1, 1)
        orders_data = []
        
        for i in range(1, num_orders + 1):
            order_date = start_date + timedelta(days=random.randint(0, 365))
            
            orders_data.append({
                'order_id': f'ORD_{i:08d}',
                'customer_id': np.random.choice(customers['customer_id']),
                'order_status': np.random.choice([
                    'delivered', 'shipped', 'processing', 'canceled'
                ], p=[0.7, 0.15, 0.1, 0.05]),
                'order_purchase_timestamp': order_date,
                'order_approved_at': order_date + timedelta(hours=random.randint(1, 48)),
                'order_delivered_carrier_date': order_date + timedelta(days=random.randint(1, 5)),
                'order_delivered_customer_date': order_date + timedelta(days=random.randint(3, 15)),
                'order_estimated_delivery_date': order_date + timedelta(days=random.randint(7, 30))
            })
        
        orders = pd.DataFrame(orders_data)
        
        # Generate Order Items
        order_items_data = []
        for order_id in orders['order_id']:
            num_items = random.randint(1, 4)
            
            for item_id in range(1, num_items + 1):
                price = random.uniform(10, 500)
                order_items_data.append({
                    'order_id': order_id,
                    'order_item_id': item_id,
                    'product_id': np.random.choice(products['product_id']),
                    'seller_id': np.random.choice(sellers['seller_id']),
                    'shipping_limit_date': orders[orders['order_id'] == order_id]['order_purchase_timestamp'].iloc[0] + timedelta(days=7),
                    'price': round(price, 2),
                    'freight_value': round(price * 0.1, 2)
                })
        
        order_items = pd.DataFrame(order_items_data)
        
        # Generate Reviews
        delivered_orders = orders[orders['order_status'] == 'delivered']['order_id']
        reviews_data = []
        
        for i, order_id in enumerate(delivered_orders.sample(n=min(800, len(delivered_orders)))):
            reviews_data.append({
                'review_id': f'REV_{i+1:08d}',
                'order_id': order_id,
                'review_score': np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.1, 0.15, 0.3, 0.4]),
                'review_comment_title': f'Review for order {order_id}',
                'review_comment_message': f'Customer feedback for {order_id}',
                'review_creation_date': orders[orders['order_id'] == order_id]['order_delivered_customer_date'].iloc[0] + timedelta(days=random.randint(0, 7)),
                'review_answer_timestamp': None
            })
        
        reviews = pd.DataFrame(reviews_data)
        
        return {
            'customers': customers,
            'products': products,
            'sellers': sellers,
            'orders': orders,
            'order_items': order_items,
            'reviews': reviews
        }

    def _load_existing_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Load existing sample data from files"""
        datasets = {}
        
        sample_files = {
            'customers': 'olist_customers_dataset.csv',
            'orders': 'olist_orders_dataset.csv',
            'order_items': 'olist_order_items_dataset.csv',
            'products': 'olist_products_dataset.csv',
            'sellers': 'olist_sellers_dataset.csv',
            'reviews': 'olist_order_reviews_dataset.csv'
        }
        
        for name, filename in sample_files.items():
            file_path = self.sample_data_dir / filename
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    datasets[name] = df
                    logger.info(f"Loaded existing sample {name}: {len(df)} records")
                except Exception as e:
                    logger.warning(f"Failed to load sample {filename}: {str(e)}")
        
        return datasets

    def _save_sample_data(self, datasets: Dict[str, pd.DataFrame]) -> None:
        """Save generated sample data to files"""
        file_mapping = {
            'customers': 'olist_customers_dataset.csv',
            'orders': 'olist_orders_dataset.csv',
            'order_items': 'olist_order_items_dataset.csv',
            'products': 'olist_products_dataset.csv',
            'sellers': 'olist_sellers_dataset.csv',
            'reviews': 'olist_order_reviews_dataset.csv'
        }
        
        for name, df in datasets.items():
            if name in file_mapping:
                file_path = self.sample_data_dir / file_mapping[name]
                try:
                    df.to_csv(file_path, index=False)
                    logger.info(f"Saved sample {name} to {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to save sample {name}: {str(e)}")

    def get_data_profile(self, datasets: Dict[str, pd.DataFrame]) -> Dict:
        """
        Generate a comprehensive data profile for extracted datasets
        
        Args:
            datasets (Dict[str, pd.DataFrame]): Extracted datasets
        
        Returns:
            Dict: Data profile information
        """
        profile = {
            'extraction_timestamp': datetime.now(),
            'total_datasets': len(datasets),
            'datasets': {}
        }
        
        for name, df in datasets.items():
            profile['datasets'][name] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / (1024**2),
                'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                'dtypes': df.dtypes.to_dict(),
                'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
            }
        
        return profile