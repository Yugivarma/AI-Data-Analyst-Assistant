-- ============================================================
-- AI Data Analyst Assistant
-- Phase 3.5 - Database Indexes
-- ============================================================

SET search_path TO analytics;


-- ============================================================
-- ORDERS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_orders_customer_id
ON orders(customer_id);

CREATE INDEX IF NOT EXISTS idx_orders_status
ON orders(order_status);

CREATE INDEX IF NOT EXISTS idx_orders_purchase_timestamp
ON orders(order_purchase_timestamp);


-- ============================================================
-- ORDER ITEMS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
ON order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_order_items_seller_id
ON order_items(seller_id);


-- ============================================================
-- PRODUCTS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_products_category
ON products(product_category_name);


-- ============================================================
-- CUSTOMERS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_customers_unique_id
ON customers(customer_unique_id);

CREATE INDEX IF NOT EXISTS idx_customers_state
ON customers(customer_state);


-- ============================================================
-- SELLERS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_sellers_state
ON sellers(seller_state);


-- ============================================================
-- PAYMENTS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_payments_type
ON order_payments(payment_type);


-- ============================================================
-- REVIEWS
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_reviews_score
ON order_reviews(review_score);


-- ============================================================
-- GEOLOCATION
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_geolocation_zip
ON geolocation(geolocation_zip_code_prefix);