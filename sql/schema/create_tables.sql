-- E-Commerce Database Schema
-- Brazilian E-Commerce Dataset Structure
-- Created for Data Pipeline Project

-- Drop existing tables if they exist (for development)
DROP TABLE IF EXISTS order_reviews CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS sellers CASCADE;
DROP TABLE IF EXISTS product_categories CASCADE;

-- Create Product Categories lookup table
CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    category_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Customers table
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50) UNIQUE,
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state CHAR(2),
    customer_country VARCHAR(50) DEFAULT 'Brazil',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Products table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(100),
    product_name_length INTEGER,
    product_description_length INTEGER,
    product_photos_qty INTEGER,
    product_weight_g DECIMAL(10,2),
    product_length_cm DECIMAL(10,2),
    product_height_cm DECIMAL(10,2),
    product_width_cm DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Add foreign key to categories
    CONSTRAINT fk_product_category 
        FOREIGN KEY (product_category_name) 
        REFERENCES product_categories(category_name)
);

-- Create Sellers table
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state CHAR(2),
    seller_country VARCHAR(50) DEFAULT 'Brazil',
    seller_rating DECIMAL(3,2) DEFAULT 0.00,
    seller_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Orders table
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_purchase_timestamp TIMESTAMP NOT NULL,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_orders_customer 
        FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id),
    
    -- Check constraints for data quality
    CONSTRAINT chk_order_status 
        CHECK (order_status IN ('processing', 'shipped', 'delivered', 'canceled', 'unavailable')),
    
    CONSTRAINT chk_order_dates 
        CHECK (order_purchase_timestamp <= order_estimated_delivery_date)
);

-- Create Order Items table
CREATE TABLE order_items (
    order_id VARCHAR(50),
    order_item_id INTEGER,
    product_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10,2) NOT NULL,
    freight_value DECIMAL(10,2) DEFAULT 0.00,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite primary key
    PRIMARY KEY (order_id, order_item_id),
    
    -- Foreign key constraints
    CONSTRAINT fk_order_items_order 
        FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE CASCADE,
    
    CONSTRAINT fk_order_items_product 
        FOREIGN KEY (product_id) 
        REFERENCES products(product_id),
    
    CONSTRAINT fk_order_items_seller 
        FOREIGN KEY (seller_id) 
        REFERENCES sellers(seller_id),
    
    -- Check constraints
    CONSTRAINT chk_positive_price 
        CHECK (price > 0),
    
    CONSTRAINT chk_positive_quantity 
        CHECK (quantity > 0),
    
    CONSTRAINT chk_non_negative_freight 
        CHECK (freight_value >= 0)
);

-- Create Order Reviews table
CREATE TABLE order_reviews (
    review_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    review_score INTEGER NOT NULL,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_reviews_order 
        FOREIGN KEY (order_id) 
        REFERENCES orders(order_id) ON DELETE CASCADE,
    
    -- Check constraint for review score
    CONSTRAINT chk_review_score 
        CHECK (review_score BETWEEN 1 AND 5)
);

-- Create indexes for better query performance
CREATE INDEX idx_customers_state ON customers(customer_state);
CREATE INDEX idx_customers_city ON customers(customer_city);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(order_status);
CREATE INDEX idx_orders_purchase_date ON orders(order_purchase_timestamp);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
CREATE INDEX idx_order_items_seller_id ON order_items(seller_id);
CREATE INDEX idx_products_category ON products(product_category_name);
CREATE INDEX idx_sellers_state ON sellers(seller_state);
CREATE INDEX idx_reviews_score ON order_reviews(review_score);
CREATE INDEX idx_reviews_creation_date ON order_reviews(review_creation_date);

-- Create views for common business queries
CREATE VIEW order_summary AS
SELECT 
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    COUNT(oi.order_item_id) as total_items,
    SUM(oi.price + oi.freight_value) as total_amount,
    AVG(oi.price) as avg_item_price
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.customer_id, o.order_status, 
         o.order_purchase_timestamp, o.order_delivered_customer_date;

CREATE VIEW customer_metrics AS
SELECT 
    c.customer_id,
    c.customer_state,
    c.customer_city,
    COUNT(o.order_id) as total_orders,
    SUM(CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END) as delivered_orders,
    SUM(oi.price + oi.freight_value) as lifetime_value,
    AVG(oi.price + oi.freight_value) as avg_order_value,
    MIN(o.order_purchase_timestamp) as first_order_date,
    MAX(o.order_purchase_timestamp) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_state, c.customer_city;

CREATE VIEW seller_performance AS
SELECT 
    s.seller_id,
    s.seller_state,
    s.seller_city,
    COUNT(DISTINCT oi.order_id) as total_orders,
    COUNT(oi.product_id) as total_items_sold,
    SUM(oi.price) as total_revenue,
    AVG(oi.price) as avg_item_price,
    AVG(r.review_score) as avg_review_score,
    COUNT(r.review_id) as total_reviews
FROM sellers s
LEFT JOIN order_items oi ON s.seller_id = oi.seller_id
LEFT JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN order_reviews r ON o.order_id = r.order_id
GROUP BY s.seller_id, s.seller_state, s.seller_city;

-- Add comments for documentation
COMMENT ON TABLE customers IS 'Customer information including location and contact details';
COMMENT ON TABLE products IS 'Product catalog with dimensions and category information';
COMMENT ON TABLE sellers IS 'Marketplace sellers with location and performance metrics';
COMMENT ON TABLE orders IS 'Order header information with status and timestamps';
COMMENT ON TABLE order_items IS 'Order line items with pricing and shipping details';
COMMENT ON TABLE order_reviews IS 'Customer reviews and ratings for completed orders';

COMMENT ON VIEW order_summary IS 'Aggregated order information with item counts and totals';
COMMENT ON VIEW customer_metrics IS 'Customer lifetime value and purchasing behavior metrics';
COMMENT ON VIEW seller_performance IS 'Seller performance metrics including revenue and ratings';