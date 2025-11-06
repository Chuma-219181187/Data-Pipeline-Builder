-- SQL Analysis Queries for E-Commerce Dataset
-- Demonstrates JOIN operations, aggregations, CRUD operations, and advanced queries

-- =============================================================================
-- 1. JOIN OPERATIONS
-- =============================================================================

-- INNER JOIN: Get orders with customer and product details
SELECT 
    o.order_id,
    c.customer_city,
    c.customer_state,
    p.product_category_name,
    oi.price,
    oi.freight_value,
    o.order_status,
    o.order_purchase_timestamp
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered'
ORDER BY o.order_purchase_timestamp DESC
LIMIT 100;

-- LEFT JOIN: All customers and their order counts (including customers with no orders)
SELECT 
    c.customer_id,
    c.customer_city,
    c.customer_state,
    COUNT(o.order_id) as order_count,
    COALESCE(SUM(oi.price + oi.freight_value), 0) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_city, c.customer_state
ORDER BY total_spent DESC;

-- RIGHT JOIN: All products and their sales (including products never sold)
SELECT 
    p.product_id,
    p.product_category_name,
    COUNT(oi.order_id) as times_sold,
    COALESCE(SUM(oi.price), 0) as total_revenue,
    COALESCE(AVG(oi.price), 0) as avg_price
FROM order_items oi
RIGHT JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY times_sold DESC;

-- FULL OUTER JOIN: Complete seller-product relationship matrix
SELECT 
    s.seller_id,
    s.seller_state,
    p.product_category_name,
    COUNT(oi.order_id) as sales_count,
    SUM(oi.price) as revenue
FROM sellers s
FULL OUTER JOIN order_items oi ON s.seller_id = oi.seller_id
FULL OUTER JOIN products p ON oi.product_id = p.product_id
GROUP BY s.seller_id, s.seller_state, p.product_category_name
ORDER BY revenue DESC NULLS LAST;

-- =============================================================================
-- 2. AGGREGATE FUNCTIONS WITH GROUP BY AND HAVING
-- =============================================================================

-- Sales by state with filtering
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT c.customer_id) as unique_customers,
    SUM(oi.price + oi.freight_value) as total_revenue,
    AVG(oi.price + oi.freight_value) as avg_order_value,
    MIN(o.order_purchase_timestamp) as first_order,
    MAX(o.order_purchase_timestamp) as last_order
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
HAVING SUM(oi.price + oi.freight_value) > 10000
ORDER BY total_revenue DESC;

-- Product category performance analysis
SELECT 
    p.product_category_name,
    COUNT(DISTINCT oi.product_id) as unique_products,
    COUNT(oi.order_id) as total_sales,
    SUM(oi.price) as category_revenue,
    AVG(oi.price) as avg_product_price,
    STDDEV(oi.price) as price_stddev,
    MIN(oi.price) as min_price,
    MAX(oi.price) as max_price
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_category_name
HAVING COUNT(oi.order_id) >= 50  -- Categories with at least 50 sales
ORDER BY category_revenue DESC;

-- Monthly sales trends
SELECT 
    EXTRACT(YEAR FROM o.order_purchase_timestamp) as year,
    EXTRACT(MONTH FROM o.order_purchase_timestamp) as month,
    COUNT(DISTINCT o.order_id) as orders_count,
    COUNT(oi.order_item_id) as items_sold,
    SUM(oi.price) as gross_revenue,
    SUM(oi.freight_value) as shipping_revenue,
    SUM(oi.price + oi.freight_value) as total_revenue,
    AVG(oi.price + oi.freight_value) as avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status IN ('delivered', 'shipped')
GROUP BY year, month
HAVING COUNT(DISTINCT o.order_id) > 10
ORDER BY year, month;

-- =============================================================================
-- 3. CRUD OPERATIONS EXAMPLES
-- =============================================================================

-- CREATE: Insert sample data
INSERT INTO product_categories (category_name, category_description) VALUES 
('Electronics', 'Electronic devices and gadgets'),
('Fashion', 'Clothing, shoes, and accessories'),
('Home & Garden', 'Home improvement and garden supplies'),
('Sports & Outdoors', 'Sports equipment and outdoor gear'),
('Books', 'Physical and digital books');

-- INSERT with conflict handling
INSERT INTO customers (customer_id, customer_unique_id, customer_city, customer_state) 
VALUES ('CUST_999999', 'UNIQ_999999', 'Test City', 'SP')
ON CONFLICT (customer_id) DO UPDATE SET
    customer_city = EXCLUDED.customer_city,
    updated_at = CURRENT_TIMESTAMP;

-- READ: Complex select with business logic
SELECT 
    customer_id,
    total_orders,
    total_spent,
    CASE 
        WHEN total_spent > 1000 THEN 'VIP'
        WHEN total_spent > 500 THEN 'Premium'
        WHEN total_spent > 100 THEN 'Regular'
        ELSE 'New'
    END as customer_tier,
    CASE 
        WHEN last_order_date > CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
        WHEN last_order_date > CURRENT_DATE - INTERVAL '90 days' THEN 'Recent'
        ELSE 'Inactive'
    END as activity_status
FROM (
    SELECT 
        c.customer_id,
        COUNT(o.order_id) as total_orders,
        COALESCE(SUM(oi.price + oi.freight_value), 0) as total_spent,
        MAX(o.order_purchase_timestamp) as last_order_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id
) customer_summary
ORDER BY total_spent DESC;

-- UPDATE: Bulk update seller ratings based on reviews
UPDATE sellers 
SET seller_rating = subquery.avg_rating,
    updated_at = CURRENT_TIMESTAMP
FROM (
    SELECT 
        s.seller_id,
        COALESCE(AVG(r.review_score::numeric), 0) as avg_rating
    FROM sellers s
    LEFT JOIN order_items oi ON s.seller_id = oi.seller_id
    LEFT JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    GROUP BY s.seller_id
) subquery
WHERE sellers.seller_id = subquery.seller_id;

-- UPDATE with conditional logic
UPDATE orders 
SET order_status = 'delivered',
    order_delivered_customer_date = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE order_status = 'shipped' 
  AND order_delivered_carrier_date IS NOT NULL
  AND order_delivered_carrier_date < CURRENT_TIMESTAMP - INTERVAL '2 days';

-- DELETE: Remove old test data (with safety constraints)
DELETE FROM order_reviews 
WHERE order_id IN (
    SELECT order_id 
    FROM orders 
    WHERE order_status = 'canceled' 
      AND order_purchase_timestamp < CURRENT_DATE - INTERVAL '2 years'
);

-- DELETE with CASCADE effect (orders will cascade to order_items and reviews)
DELETE FROM orders 
WHERE order_status = 'canceled' 
  AND order_purchase_timestamp < CURRENT_DATE - INTERVAL '2 years'
  AND customer_id LIKE 'TEST_%';

-- =============================================================================
-- 4. SUBQUERIES AND COMMON TABLE EXPRESSIONS (CTEs)
-- =============================================================================

-- Subquery: Find customers who spent more than average
SELECT 
    customer_id,
    customer_state,
    total_spent
FROM (
    SELECT 
        c.customer_id,
        c.customer_state,
        SUM(oi.price + oi.freight_value) as total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_state
) customer_totals
WHERE total_spent > (
    SELECT AVG(customer_spend)
    FROM (
        SELECT SUM(oi.price + oi.freight_value) as customer_spend
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.customer_id
    ) avg_calculation
)
ORDER BY total_spent DESC;

-- CTE: Customer lifecycle analysis
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        c.customer_state,
        COUNT(o.order_id) as order_count,
        MIN(o.order_purchase_timestamp) as first_order,
        MAX(o.order_purchase_timestamp) as last_order,
        SUM(oi.price + oi.freight_value) as total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_state
),
customer_segments AS (
    SELECT 
        *,
        EXTRACT(DAYS FROM (last_order - first_order)) as customer_lifespan_days,
        CASE 
            WHEN order_count = 1 THEN 'One-time'
            WHEN order_count BETWEEN 2 AND 5 THEN 'Occasional'
            WHEN order_count BETWEEN 6 AND 15 THEN 'Regular'
            ELSE 'Frequent'
        END as purchase_frequency,
        CASE 
            WHEN total_spent < 100 THEN 'Low Value'
            WHEN total_spent < 500 THEN 'Medium Value'
            WHEN total_spent < 1000 THEN 'High Value'
            ELSE 'VIP'
        END as value_segment
    FROM customer_orders
)
SELECT 
    customer_state,
    purchase_frequency,
    value_segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_spent,
    AVG(customer_lifespan_days) as avg_lifespan_days
FROM customer_segments
GROUP BY customer_state, purchase_frequency, value_segment
ORDER BY customer_state, customer_count DESC;

-- Recursive CTE: Product category hierarchy (if we had hierarchical categories)
WITH RECURSIVE category_hierarchy AS (
    -- Base case: top-level categories
    SELECT 
        category_name,
        category_name as root_category,
        0 as level
    FROM product_categories
    WHERE category_name NOT LIKE '%:%'  -- Assuming ':' separates hierarchy levels
    
    UNION ALL
    
    -- Recursive case: subcategories
    SELECT 
        pc.category_name,
        ch.root_category,
        ch.level + 1
    FROM product_categories pc
    JOIN category_hierarchy ch ON pc.category_name LIKE ch.category_name || ':%'
)
SELECT * FROM category_hierarchy ORDER BY root_category, level, category_name;

-- =============================================================================
-- 5. ADVANCED FILTERS, SORTING, AND TRANSFORMATIONS
-- =============================================================================

-- Window functions for ranking and analytics
SELECT 
    seller_id,
    seller_state,
    total_revenue,
    order_count,
    ROW_NUMBER() OVER (PARTITION BY seller_state ORDER BY total_revenue DESC) as state_rank,
    RANK() OVER (ORDER BY total_revenue DESC) as overall_rank,
    DENSE_RANK() OVER (ORDER BY total_revenue DESC) as dense_rank,
    PERCENT_RANK() OVER (ORDER BY total_revenue) as percentile_rank,
    LAG(total_revenue) OVER (ORDER BY total_revenue DESC) as prev_seller_revenue,
    LEAD(total_revenue) OVER (ORDER BY total_revenue DESC) as next_seller_revenue,
    SUM(total_revenue) OVER (PARTITION BY seller_state) as state_total_revenue,
    AVG(total_revenue) OVER (PARTITION BY seller_state) as state_avg_revenue
FROM (
    SELECT 
        s.seller_id,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) as order_count,
        SUM(oi.price) as total_revenue
    FROM sellers s
    JOIN order_items oi ON s.seller_id = oi.seller_id
    GROUP BY s.seller_id, s.seller_state
) seller_metrics
WHERE total_revenue > 1000
ORDER BY total_revenue DESC;

-- Advanced date filtering and transformations
SELECT 
    DATE_TRUNC('quarter', o.order_purchase_timestamp) as quarter,
    COUNT(DISTINCT o.order_id) as orders,
    SUM(oi.price + oi.freight_value) as revenue,
    AVG(oi.price + oi.freight_value) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(oi.price + oi.freight_value) / COUNT(DISTINCT o.customer_id) as revenue_per_customer
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_purchase_timestamp >= CURRENT_DATE - INTERVAL '2 years'
  AND o.order_status IN ('delivered', 'shipped')
GROUP BY quarter
ORDER BY quarter;

-- Text processing and pattern matching
SELECT 
    review_id,
    order_id,
    review_score,
    LENGTH(review_comment_message) as comment_length,
    CASE 
        WHEN review_comment_message ILIKE '%excellent%' OR 
             review_comment_message ILIKE '%amazing%' OR 
             review_comment_message ILIKE '%perfect%' THEN 'Positive Language'
        WHEN review_comment_message ILIKE '%terrible%' OR 
             review_comment_message ILIKE '%awful%' OR 
             review_comment_message ILIKE '%horrible%' THEN 'Negative Language'
        ELSE 'Neutral Language'
    END as sentiment_category,
    SPLIT_PART(review_comment_title, ' ', 1) as first_word,
    REGEXP_REPLACE(review_comment_message, '[^a-zA-Z0-9\s]', '', 'g') as cleaned_comment
FROM order_reviews
WHERE review_comment_message IS NOT NULL
  AND LENGTH(review_comment_message) > 10
ORDER BY review_creation_date DESC
LIMIT 500;