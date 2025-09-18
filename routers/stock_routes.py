from fastapi import APIRouter, HTTPException
from typing import List

from model.stock_data import StockFundamentalData

router = APIRouter()

@router.get("/stock/{symbol}", response_model=StockFundamentalData)
async def get_stock_fundamental_data(symbol: str):
    # Simulate fetching data from a database or external API
    # Get one fake stock data by symbol
    fake_stock_db = {
        "AAPL": StockFundamentalData(
            symbol="AAPL",
            company_name="Apple Inc.",
            market_cap=2.5e12,
            pe_ratio=28.5,
            dividend_yield=0.006,
            eps=5.11,
            revenue=365.8e9,
            net_income=86.9e9,
            debt_to_equity=1.5,
            return_on_equity=0.75
        ),
        "MSFT": StockFundamentalData(
            symbol="MSFT",
            company_name="Microsoft Corporation",
            market_cap=2.0e12,
            pe_ratio=35.0,
            dividend_yield=0.008,
            eps=8.05,
            revenue=168.1e9,
            net_income=61.3e9,
            debt_to_equity=0.7,
            return_on_equity=0.40
        )
    }
    stock_data = fake_stock_db.get(symbol.upper())

    if not stock_data:
        raise HTTPException(status_code=404, detail="Stock not found")

    return stock_data
