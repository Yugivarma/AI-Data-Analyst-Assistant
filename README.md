# AI Data Analyst Assistant

An AI-powered analytics platform that converts natural-language questions into SQL, executes them against PostgreSQL, generates visualizations, and provides business insights.

## Overview

This project is a full-stack AI Data Analyst Assistant built around the Olist e-commerce dataset. Users can ask business questions in natural language, and the application uses Gemini to generate SQL, validates the SQL for safety, executes it against PostgreSQL, and returns results, visualizations, and concise insights.

## Architecture

User -> React Frontend -> FastAPI Backend -> Gemini -> SQL Validation -> PostgreSQL -> Results -> Visualization + Insight

## Key Features

- Natural-language data analysis
- AI-generated PostgreSQL SQL
- Read-only SQL validation
- PostgreSQL analytics database
- Analytical database views
- Query result limits and statement timeouts
- Automatic visualization selection
- AI-generated business insights
- FastAPI REST API
- React + Vite frontend
- Recharts visualizations
- Automated backend tests

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Gemini API
- React
- Vite
- Recharts
- Pytest

## Dataset

The project uses the Brazilian Olist e-commerce dataset, containing information about customers, orders, order items, payments, reviews, products, sellers, geolocation, and product categories.

Raw datasets are kept outside Git tracking.

## Data Pipeline

1. Extract raw CSV datasets
2. Assess data quality
3. Clean and transform data
4. Validate primary keys, foreign keys, data types, ranges, and relationships
5. Load cleaned data into PostgreSQL
6. Create analytical views
7. Expose analytics through FastAPI
8. Generate SQL from natural-language questions
9. Validate and execute generated SQL
10. Return results, charts, and insights

## PostgreSQL Analytics Layer

The database contains nine analytics tables and five analytical views:

- monthly_sales
- category_performance
- seller_performance
- customer_summary
- order_delivery_performance

The analytical views provide reusable business metrics for the AI query layer.

## Example Questions

- What are the top 5 product categories by total revenue?
- Which sellers generate the most revenue?
- How have sales changed over time?
- Which categories have the highest average item price?
- What is the average order value for customers?
- How long does delivery usually take?

## AI Query Workflow

1. User submits a natural-language question.
2. Gemini generates a PostgreSQL SELECT query using the known database schema.
3. The backend validates the generated SQL.
4. Only read-only queries against the analytics schema are allowed.
5. PostgreSQL executes the validated query.
6. Results are limited to prevent excessive responses.
7. A visualization type is selected automatically.
8. Gemini generates a concise insight based only on the returned database results.

## Security and Reliability

The application includes safeguards around AI-generated SQL:

- Only SELECT statements are accepted.
- Multiple SQL statements are rejected.
- SQL comments are rejected.
- Write and administrative commands are blocked.
- Access to PostgreSQL system schemas is blocked.
- Dangerous PostgreSQL functions such as pg_sleep and file-access functions are blocked.
- Query results are capped at 500 rows.
- PostgreSQL statement execution has a 10-second timeout.
- Gemini-generated SQL is validated before execution.

## Testing

The backend includes automated tests covering SQL validation and security rules.

Current test result: **15 tests passed**.

## Project Structure

backend/
  - api/
  - auth/
  - database/
  - llm/
  - services/
  - utils/
  - main.py

database/
  - schema.sql
  - analytical_views.sql

etl/
  - extract.py
  - quality_check.py
  - clean.py
  - validate.py
  - load_database.py

frontend/
  - frontend/

tests/

## Local Setup

Create a Python virtual environment and install the project dependencies.

Configure PostgreSQL and create the required database.

Create a local .env file containing the PostgreSQL connection settings and Gemini API key.

Start the backend with:

    .\venv\Scripts\python.exe -m uvicorn backend.main:app --reload

Start the frontend from the React application directory with:

    npm.cmd run dev

The development application runs locally on the FastAPI and Vite development servers.

## API Endpoints

- GET /health
- GET /test-database
- GET /analytics/monthly-sales
- GET /analytics/category-performance
- GET /analytics/seller-performance
- GET /analytics/customer-summary
- GET /analytics/order-delivery-performance
- POST /query

## Example AI Result

For the question `What are the top 5 product categories by total revenue?`, the system generates SQL against the category performance view, executes it in PostgreSQL, and returns the ranked categories together with revenue values, a visualization, and a concise business insight.

## Future Improvements

- User authentication
- Conversation history
- More advanced visualization recommendations
- Query caching
- Production deployment
- Additional analytical views
- More comprehensive integration tests

## Project Goal

The goal of this project is to demonstrate how modern AI can be combined with data engineering, SQL, backend APIs, databases, and frontend development to create a practical natural-language analytics application.

## Repository

GitHub: https://github.com/Yugivarma/AI-Data-Analyst-Assistant
