from pydantic import BaseModel
from typing import Dict, List, Optional
from beanie import Document

# Beanie Document model for MongoDB
class StockFundamentalDataMongoDB(Document):
    symbol: str
    company_name: Optional[str]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    eps: Optional[float]
    revenue: Optional[float]
    net_income: Optional[float]
    return_on_equity: Optional[float]
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    total_shareholder_equity: Optional[float]
    total_current_assets: Optional[float]
    total_current_liabilities: Optional[float]
    long_term_debt: Optional[float]
    cash_and_cash_equivalents: Optional[float]

    class Settings:
        name = "stock_fundamentals"