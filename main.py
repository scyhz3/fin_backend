from fastapi import FastAPI
from routers import stock_routes

app = FastAPI()

app.include_router(stock_routes.router, prefix="/api", tags=["stocks"])

@app.get("/")
async def root():
    return {"message": "Hello World"}