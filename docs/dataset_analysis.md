# Dataset Selection & Analysis

## Recommended Dataset: E-commerce Sales Data

### Dataset Source: Kaggle - "Brazilian E-Commerce Public Dataset by Olist"
- **URL:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- **Size:** ~100,000 orders, 500,000+ reviews
- **License:** CC BY-NC-SA 4.0
- **Format:** Multiple CSV files

### Why This Dataset is Perfect:

1. **Multiple Related Tables** - Perfect for JOIN operations
2. **Large Scale** - 100K+ records for performance testing
3. **Real Business Logic** - Actual e-commerce scenarios
4. **Data Quality Issues** - Great for transformation challenges
5. **Rich Analytics** - Customer behavior, sales trends, geography

### Dataset Structure:

#### Core Tables:
1. **orders** - Order information
   - order_id (PK)
   - customer_id (FK)
   - order_status
   - order_purchase_timestamp
   - order_delivered_timestamp

2. **customers** - Customer information
   - customer_id (PK)
   - customer_city
   - customer_state
   - customer_zip_code_prefix

3. **order_items** - Items in each order
   - order_id (FK)
   - order_item_id
   - product_id (FK)
   - seller_id (FK)
   - price
   - freight_value

4. **products** - Product catalog
   - product_id (PK)
   - product_category_name
   - product_name_length
   - product_description_length
   - product_weight_g

5. **sellers** - Seller information
   - seller_id (PK)
   - seller_city
   - seller_state
   - seller_zip_code_prefix

6. **order_reviews** - Customer reviews
   - review_id (PK)
   - order_id (FK)
   - review_score
   - review_comment_title
   - review_comment_message

### Alternative Dataset Options:

#### Option 2: Northwind Database
- **Source:** Microsoft Sample Database
- **Size:** ~3,000 orders
- **Pros:** Well-documented, classic business scenario
- **Tables:** Customers, Orders, Products, Categories, Suppliers

#### Option 3: NYC Taxi Trip Data
- **Source:** NYC Open Data
- **Size:** Millions of records
- **Pros:** Time-series analysis, geospatial data
- **Challenges:** Very large size, requires sampling

#### Option 4: World University Rankings
- **Source:** Kaggle/Times Higher Education
- **Size:** 2,000+ universities
- **Pros:** Educational data, multiple ranking factors
- **Tables:** Universities, Rankings, Countries, Subjects

### SQL Analysis Opportunities:

#### JOIN Operations:
- INNER JOIN: Orders with order items and products
- LEFT JOIN: Customers with their orders (including customers with no orders)
- RIGHT JOIN: Products with their sales (including unsold products)

#### Aggregate Functions:
- Total sales by state/city
- Average order value per customer
- Product performance metrics
- Monthly/quarterly revenue trends

#### Advanced Queries:
- Customer lifetime value calculation
- Product recommendation based on purchase history
- Delivery performance analysis
- Seller performance ranking

### ETL Pipeline Opportunities:

#### Extract:
- Multiple CSV files to combine
- Data validation and schema checking
- Error handling for corrupted records

#### Transform:
- Date format standardization
- Geographic data normalization
- Price calculations (with tax, freight)
- Data quality scoring
- Customer segmentation

#### Load:
- Dimensional modeling (fact and dimension tables)
- Incremental loading strategies
- Data warehousing best practices

### Download Instructions:

1. **Visit Kaggle Dataset:**
   ```
   https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
   ```

2. **Download Files:**
   - olist_customers_dataset.csv
   - olist_orders_dataset.csv
   - olist_order_items_dataset.csv
   - olist_products_dataset.csv
   - olist_sellers_dataset.csv
   - olist_order_reviews_dataset.csv

3. **Place in Data Directory:**
   ```
   data-pipeline-project/data/raw/
   ```

### Next Steps:

1. Download the selected dataset
2. Create database schema based on table relationships
3. Design ETL pipeline for data processing
4. Implement SQL analysis queries

**Recommendation: Go with the Brazilian E-commerce dataset** - it provides the perfect balance of complexity, real-world relevance, and learning opportunities for this project.