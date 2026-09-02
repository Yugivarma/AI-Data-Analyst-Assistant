# AI Data Analyst Assistant - Data Dictionary

## Project Overview

This project uses the Olist Brazilian E-commerce Dataset to build an AI-powered analytics assistant capable of answering business questions using natural language.

The database follows a relational schema where customers place orders, orders contain products sold by sellers, customers make payments, and leave reviews after delivery.

---

# Database Relationships

Customers
        │
        ▼
Orders
        │
        ├──────────────► Order Items
        │                     │
        │                     ├────────► Products
        │                     │
        │                     └────────► Sellers
        │
        ├──────────────► Payments
        │
        └──────────────► Reviews

---

# Table: customers

## Purpose

Stores customer demographic and location information.

Each row represents one customer account.

## Primary Key

customer_id

## Used For

- Customer segmentation
- Customer distribution
- Regional analysis
- Repeat customer analysis

| Column | Description |
|---------|-------------|
| customer_id | Unique customer identifier |
| customer_unique_id | Unique person identifier across multiple orders |
| customer_zip_code_prefix | ZIP code prefix |
| customer_city | Customer city |
| customer_state | Customer state |

Business Notes

- One customer can place multiple orders.
- customer_unique_id represents the actual person.

---

# Table: orders

## Purpose

Stores the complete lifecycle of every order.

## Primary Key

order_id

## Foreign Key

customer_id → customers.customer_id

## Used For

- Order tracking
- Delivery analysis
- Revenue analysis
- Order status reporting

| Column | Description |
|---------|-------------|
| order_id | Unique order identifier |
| customer_id | Customer who placed the order |
| order_status | Current order status |
| order_purchase_timestamp | Purchase timestamp |
| order_approved_at | Payment approval timestamp |
| order_delivered_carrier_date | Date shipped to carrier |
| order_delivered_customer_date | Customer delivery date |
| order_estimated_delivery_date | Estimated delivery date |

Business Notes

- NULL delivery dates are valid for orders that were not yet delivered.
- This table is the central table of the database.

---

# Table: order_items

## Purpose

Stores products included in each order.

## Composite Primary Key

(order_id, order_item_id)

## Foreign Keys

order_id → orders.order_id

product_id → products.product_id

seller_id → sellers.seller_id

## Used For

- Revenue calculation
- Product analysis
- Seller performance
- Basket analysis

| Column | Description |
|---------|-------------|
| order_id | Order identifier |
| order_item_id | Item number inside an order |
| product_id | Purchased product |
| seller_id | Seller providing the product |
| shipping_limit_date | Shipping deadline |
| price | Product price |
| freight_value | Shipping cost |

Business Notes

- One order can contain multiple products.
- Revenue calculations are based on this table.

---

# Table: products

## Purpose

Contains product metadata.

## Primary Key

product_id

## Used For

- Category analysis
- Product popularity
- Product characteristics

| Column | Description |
|---------|-------------|
| product_id | Product identifier |
| product_category_name | Product category |
| product_name_lenght | Product name length |
| product_description_lenght | Product description length |
| product_photos_qty | Number of product images |
| product_weight_g | Product weight |
| product_length_cm | Product length |
| product_height_cm | Product height |
| product_width_cm | Product width |

Business Notes

- Missing categories are standardized as "unknown" in the processed data.

---

# Table: sellers

## Purpose

Stores seller information.

## Primary Key

seller_id

## Used For

- Seller performance
- Regional sales
- Shipping analysis

| Column | Description |
|---------|-------------|
| seller_id | Seller identifier |
| seller_zip_code_prefix | ZIP code prefix |
| seller_city | Seller city |
| seller_state | Seller state |

Business Notes

- One seller can sell many products.

---

# Table: order_payments

## Purpose

Stores payment information for every order.

## Composite Primary Key

(order_id, payment_sequential)

## Foreign Key

order_id → orders.order_id

## Used For

- Revenue
- Payment analysis
- Installment analysis

| Column | Description |
|---------|-------------|
| order_id | Order identifier |
| payment_sequential | Payment sequence |
| payment_type | Payment method |
| payment_installments | Number of installments |
| payment_value | Payment amount |

Business Notes

- Some orders contain multiple payment records.

---

# Table: order_reviews

## Purpose

Stores customer feedback.

## Primary Key

review_id

## Foreign Key

order_id → orders.order_id

## Used For

- Customer satisfaction
- Sentiment analysis
- Product quality analysis

| Column | Description |
|---------|-------------|
| review_id | Review identifier |
| order_id | Related order |
| review_score | Rating (1–5) |
| review_comment_title | Review title |
| review_comment_message | Review text |
| review_creation_date | Review creation date |
| review_answer_timestamp | Seller response timestamp |

Business Notes

- Missing review comments are expected and should remain NULL.

---

# Table: geolocation

## Purpose

Maps ZIP code prefixes to geographic coordinates.

## Primary Key

No unique primary key in the raw dataset.

## Used For

- Geographic visualization
- Customer mapping
- Seller mapping

| Column | Description |
|---------|-------------|
| geolocation_zip_code_prefix | ZIP code prefix |
| geolocation_lat | Latitude |
| geolocation_lng | Longitude |
| geolocation_city | City |
| geolocation_state | State |

Business Notes

- Duplicate rows were removed during the ETL process.
- Invalid coordinates outside Brazil were removed during cleaning.

---

# Table: product_category_name_translation

## Purpose

Translates Portuguese category names into English.

## Primary Key

product_category_name

## Used For

- Dashboard readability
- AI-generated insights
- Reporting

| Column | Description |
|---------|-------------|
| product_category_name | Portuguese category |
| product_category_name_english | English category |

Business Notes

- Used when displaying category names to users.

---

# Business KPIs Supported

The database can answer questions such as:

- Monthly Revenue
- Revenue by State
- Top Customers
- Top Products
- Revenue by Product Category
- Seller Performance
- Delivery Performance
- Average Delivery Time
- Payment Method Distribution
- Installment Analysis
- Customer Satisfaction
- Review Score Distribution
- Repeat Customers
- Customer Lifetime Value (Approximation)