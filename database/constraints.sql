-- ============================================================
-- AI Data Analyst Assistant
-- Phase 3.4 - Database Constraints
-- ============================================================

SET search_path TO analytics;


-- ============================================================
-- ORDERS
-- ============================================================

ALTER TABLE orders
ADD CONSTRAINT chk_orders_status
CHECK (
    order_status IN (
        'created',
        'approved',
        'invoiced',
        'processing',
        'shipped',
        'delivered',
        'canceled',
        'unavailable'
    )
);


-- ============================================================
-- CUSTOMERS
-- ============================================================

ALTER TABLE customers
ADD CONSTRAINT chk_customer_state
CHECK (
    customer_state IS NULL
    OR customer_state ~ '^[A-Z]{2}$'
);


-- ============================================================
-- SELLERS
-- ============================================================

ALTER TABLE sellers
ADD CONSTRAINT chk_seller_state
CHECK (
    seller_state IS NULL
    OR seller_state ~ '^[A-Z]{2}$'
);


-- ============================================================
-- GEOLOCATION
-- ============================================================

ALTER TABLE geolocation
ADD CONSTRAINT chk_geolocation_latitude
CHECK (
    geolocation_lat BETWEEN -90 AND 90
);

ALTER TABLE geolocation
ADD CONSTRAINT chk_geolocation_longitude
CHECK (
    geolocation_lng BETWEEN -180 AND 180
);


-- ============================================================
-- PRODUCT MEASUREMENTS
-- ============================================================

ALTER TABLE products
ADD CONSTRAINT chk_product_weight
CHECK (
    product_weight_g IS NULL
    OR product_weight_g >= 0
);

ALTER TABLE products
ADD CONSTRAINT chk_product_length
CHECK (
    product_length_cm IS NULL
    OR product_length_cm >= 0
);

ALTER TABLE products
ADD CONSTRAINT chk_product_height
CHECK (
    product_height_cm IS NULL
    OR product_height_cm >= 0
);

ALTER TABLE products
ADD CONSTRAINT chk_product_width
CHECK (
    product_width_cm IS NULL
    OR product_width_cm >= 0
);


-- ============================================================
-- PRODUCT COUNTS
-- ============================================================

ALTER TABLE products
ADD CONSTRAINT chk_product_photos
CHECK (
    product_photos_qty IS NULL
    OR product_photos_qty >= 0
);


-- ============================================================
-- ORDER ITEMS
-- ============================================================

ALTER TABLE order_items
ADD CONSTRAINT chk_order_item_id
CHECK (
    order_item_id > 0
);

ALTER TABLE order_items
ADD CONSTRAINT chk_item_price
CHECK (
    price IS NULL OR price >= 0
);

ALTER TABLE order_items
ADD CONSTRAINT chk_freight_value
CHECK (
    freight_value IS NULL OR freight_value >= 0
);


-- ============================================================
-- PAYMENTS
-- ============================================================

ALTER TABLE order_payments
ADD CONSTRAINT chk_payment_sequential
CHECK (
    payment_sequential > 0
);

ALTER TABLE order_payments
ADD CONSTRAINT chk_payment_installments
CHECK (
    payment_installments IS NULL
    OR payment_installments > 0
);

ALTER TABLE order_payments
ADD CONSTRAINT chk_payment_value
CHECK (
    payment_value IS NULL
    OR payment_value >= 0
);

