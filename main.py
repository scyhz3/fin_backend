from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import stock_routes
from model.stock_data import StockFundamentalDataMongoDB
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

@asynccontextmanager
async def lifespan(_: FastAPI):
    print("connecting to MongoDB...")
    client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)  # Add a timeout
    await client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    await init_beanie(database=client.get_database("financial_data"),
                      document_models=[StockFundamentalDataMongoDB])
    print("Beanie initialized successfully.")
    yield
    # Optionally, add cleanup code here

app = FastAPI(lifespan=lifespan)
app.include_router(stock_routes.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Hello World"}
