from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from typing import List

from backend.api.models import (
    HealthResponse,
    DatabaseTestResponse,
    MonthlySalesResponse,
    CategoryPerformanceResponse,
    SellerPerformanceResponse,
    CustomerSummaryResponse,
    OrderDeliveryPerformanceResponse,
    QueryRequest,
    QueryResponse
)

from backend.database.connection import engine, get_db
from backend.services.database_service import execute_query
from backend.services.analytics_service import get_monthly_sales, get_category_performance, get_seller_performance,get_customer_summary,get_order_delivery_performance
# pyrefly: ignore [missing-import]
from backend.services.query_service import answer_question

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Welcome to AI Data Analyst Assistant"
    }


@router.get("/health", response_model=HealthResponse)
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/test-database", response_model=DatabaseTestResponse)
def test_database(db: Session = Depends(get_db)):
    query = """
        SELECT
            COUNT(*) AS total_orders
        FROM analytics.orders
    """

    results = execute_query(db, query)

    return results[0]


@router.get(
    "/analytics/monthly-sales",
    response_model=List[MonthlySalesResponse]
)
def monthly_sales(db: Session = Depends(get_db)):
    return get_monthly_sales(db)

@router.get(
    "/analytics/category-performance",
    response_model=List[CategoryPerformanceResponse]
)
def category_performance(db: Session = Depends(get_db)):
    return get_category_performance(db)

@router.get(
    "/analytics/seller-performance",
    response_model=List[SellerPerformanceResponse]
)
def seller_performance(db: Session = Depends(get_db)):
    return get_seller_performance(db)

@router.get(
    "/analytics/customer-summary",
    response_model=List[CustomerSummaryResponse]
)
def customer_summary(db: Session = Depends(get_db)):
    return get_customer_summary(db)

@router.get(
    "/analytics/order-delivery-performance",
    response_model=List[OrderDeliveryPerformanceResponse]
)
def order_delivery_performance(db: Session = Depends(get_db)):
    return get_order_delivery_performance(db)

@router.post("/query", response_model=QueryResponse)
def query_data(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Accept a natural-language question and return
    SQL, database results, and a business insight.
    """

    return answer_question(
        db=db,
        question=request.question
    )