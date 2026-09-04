from datetime import date, datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str


class DatabaseTestResponse(BaseModel):
    total_orders: int


class MonthlySalesResponse(BaseModel):
    month: date
    total_orders: int
    total_items: int
    product_revenue: float
    freight_revenue: float
    total_revenue: float


class CategoryPerformanceResponse(BaseModel):
    category: str
    total_orders: int
    total_items: int
    product_revenue: float
    freight_revenue: float
    total_revenue: float
    average_item_price: float


class SellerPerformanceResponse(BaseModel):
    seller_id: str
    seller_city: str
    seller_state: str
    total_orders: int
    total_items: int
    product_revenue: float
    freight_revenue: float
    total_revenue: float
    average_item_price: float


class CustomerSummaryResponse(BaseModel):
    customer_unique_id: str
    customer_city: str
    customer_state: str
    total_orders: int
    first_order_date: datetime
    last_order_date: datetime
    product_spend: float
    freight_spend: float
    total_spend: float
    average_order_value: float


class OrderDeliveryPerformanceResponse(BaseModel):
    order_id: str
    customer_id: str
    order_status: str
    order_purchase_timestamp: datetime
    order_delivered_customer_date: datetime | None
    order_estimated_delivery_date: datetime
    delivery_days: float | None
    delivery_delay_days: float | None

class QueryRequest(BaseModel):
    question: str


class VisualizationResponse(BaseModel):
    type: str
    x_key: str | None
    y_key: str | None
    data: list[dict]


class QueryResponse(BaseModel):
    question: str
    sql: str
    results: list[dict]
    insight: str
    visualization: VisualizationResponse