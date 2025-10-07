from fastapi import APIRouter, HTTPException
from typing import List
from server import stock_server

from model.stock_data import StockFundamentalDataMongoDB

router = APIRouter()

@router.get("/stock/{symbol}",
         response_model=StockFundamentalDataMongoDB,
         tags=["Stocks"])
async def get_stock_fundamental_data(symbol: str):

    stock_data = await stock_server.get_stock_fundamental_data(symbol)
    # If no data is returned, send a 404 "Not Found" response
    if not stock_data:
        raise HTTPException(
            status_code=404,
            detail=f"Fundamental data for symbol '{symbol}' not found."
        )

    return stock_data

# Read stock data from the database
@router.get("/stock/db/{symbol}",
         response_model=StockFundamentalDataMongoDB,
         tags=["Stocks"])
async def read_stock_fundamental_data(symbol: str):
    stock_data = await stock_server.read_stock_fundamental_data(symbol)
    # If no data is returned, send a 404 "Not Found" response
    if not stock_data:
        raise HTTPException(
            status_code=404,
            detail=f"Fundamental data for symbol '{symbol}' not found in database."
        )

    return stock_data
