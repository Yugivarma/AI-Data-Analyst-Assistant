from sqlalchemy.orm import Session

from backend.services.database_service import execute_query


def get_monthly_sales(db: Session):
    query = """
        SELECT
            month,
            total_orders,
            total_items,
            product_revenue,
            freight_revenue,
            total_revenue
        FROM analytics.monthly_sales
        ORDER BY month
    """

    return execute_query(db, query)


def get_category_performance(db: Session):
    query = """
        SELECT
            category,
            total_orders,
            total_items,
            product_revenue,
            freight_revenue,
            total_revenue,
            average_item_price
        FROM analytics.category_performance
        ORDER BY total_revenue DESC
    """

    return execute_query(db, query)


def get_seller_performance(db: Session):
    query = """
        SELECT
            seller_id,
            seller_city,
            seller_state,
            total_orders,
            total_items,
            product_revenue,
            freight_revenue,
            total_revenue,
            average_item_price
        FROM analytics.seller_performance
        ORDER BY total_revenue DESC
    """
    return execute_query(db, query)


def get_customer_summary(db: Session):
    query = """
        SELECT
            customer_unique_id,
            customer_city,
            customer_state,
            total_orders,
            first_order_date,
            last_order_date,
            product_spend,
            freight_spend,
            total_spend,
            average_order_value
        FROM analytics.customer_summary
        ORDER BY total_spend DESC
    """
    return execute_query(db, query)


def get_order_delivery_performance(db: Session):
    query = """
        SELECT
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_delivered_customer_date,
            order_estimated_delivery_date,
            delivery_days,
            delivery_delay_days
        FROM analytics.order_delivery_performance
        ORDER BY delivery_delay_days DESC NULLS LAST
    """
    return execute_query(db, query)