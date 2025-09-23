from pydantic import BaseModel
from typing import Dict, List, Optional

class StockFundamentalData(BaseModel):
    symbol: str
    company_name: Optional[str]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    eps: Optional[float]
    revenue: Optional[float]
    net_income: Optional[float]
    return_on_equity: Optional[float]
    totalAssets: Optional[float]
    totalLiabilities: Optional[float]
    totalShareholderEquity: Optional[float]
    totalCurrentAssets: Optional[float]
    totalCurrentLiabilities: Optional[float]
    longTermDebt: Optional[float]
    cashAndCashEquivalentsAtCarryingValue: Optional[float]