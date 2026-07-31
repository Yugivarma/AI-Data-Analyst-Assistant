from fastapi import FastAPI

app = FastAPI(
    title="AI Data Analyst Assistant",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Data Analyst Assistant"
    }
