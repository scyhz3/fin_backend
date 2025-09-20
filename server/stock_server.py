from typing import Optional
import requests
import os
from dotenv import load_dotenv
import logging

from model.stock_data import StockFundamentalData

# -- Logging Configuration --
# Configure basic logging to console (optional, but ensures console output)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get a logger instance for the current module
logger = logging.getLogger(__name__)

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
MAIN_URL = "https://www.alphavantage.co/query"


# --- Helper Function ---
def safe_float_conversion(value: Optional[str]) -> Optional[float]:
    """
    A safe conversion function to convert API string responses to floats.
    It correctly handles 'None' strings and potential conversion errors.
    """
    if value is None or value == 'None':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


# --- Get Stock data Function ---
async def get_stock_fundamental_data(symbol: str) -> Optional[StockFundamentalData]:
    """
    Fetches fundamental stock data and returns a Pydantic model instance.
    Returns None if the stock is not found or an API error occurs.
    """
    logger.info(f"Fetching fundamental data for symbol: {symbol}")
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": API_KEY
    }

    try:
        response = requests.get(MAIN_URL, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP errors (e.g., 4xx or 5xx)
        data = response.json()

        # if the symbol is not found or another error occurs.
        if not data or "Error Message" in data:
            print(f"Error fetching data for {symbol}: {data.get('Error Message', 'Empty response')}")
            return None

        # map the API
        stock_data = StockFundamentalData(
            symbol=data.get('Symbol'),
            company_name=data.get('Name'),
            market_cap=safe_float_conversion(data.get('MarketCapitalization')),
            pe_ratio=safe_float_conversion(data.get('PERatio')),
            dividend_yield=safe_float_conversion(data.get('DividendYield')),
            eps=safe_float_conversion(data.get('EPS')),
            revenue=safe_float_conversion(data.get('RevenueTTM')),  # Use TTM (Trailing Twelve Months) revenue
            net_income=None,  # 'OVERVIEW' endpoint doesn't directly provide Net Income
            debt_to_equity=None,  # 'OVERVIEW' endpoint doesn't directly provide Debt to Equity ratio
            return_on_equity=safe_float_conversion(data.get('ReturnOnEquityTTM'))
        )

        return stock_data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during API request: {e}")
        return None