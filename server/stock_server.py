from typing import Optional
import requests
import os
from dotenv import load_dotenv
import logging
import httpx

from model.stock_data import StockFundamentalDataMongoDB
from utils.utils import safe_float_conversion

# -- Logging Configuration --
# Configure basic logging to console (optional, but ensures console output)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get a logger instance for the current module
logger = logging.getLogger(__name__)

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
MAIN_URL = "https://www.alphavantage.co/query"


# --- Read Stock Data Function ---
async def read_stock_fundamental_data(symbol: str) -> Optional[StockFundamentalDataMongoDB]:
    """
    Reads fundamental stock data from the database.
    Returns None if the stock is not found.
    """
    logger.info(f"Reading fundamental data for symbol: {symbol} from database.")
    stock_document = await StockFundamentalDataMongoDB.find_one(StockFundamentalDataMongoDB.symbol == symbol)
    if stock_document:
        logger.info(f"Found document for {symbol} in database.")
    else:
        logger.info(f"No document found for {symbol} in database.")
    return stock_document



# --- Get Stock data Function ---
async def get_stock_fundamental_data(symbol: str) -> Optional[StockFundamentalDataMongoDB]:
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

        balance_sheet_data = await fetch_balance_sheet(symbol)
        income_statement_data = await fetch_income_statement(symbol)

        # Guard against missing data from secondary calls
        if not balance_sheet_data or not income_statement_data:
            logger.error(f"Could not fetch balance sheet or income statement for {symbol}")
            return None

        api_data = {
            "symbol": data.get('Symbol'),
            "company_name": data.get('Name'),
            "market_cap": safe_float_conversion(data.get('MarketCapitalization')),
            "pe_ratio": safe_float_conversion(data.get('PERatio')),
            "dividend_yield": safe_float_conversion(data.get('DividendYield')),
            "eps": safe_float_conversion(data.get('EPS')),
            "revenue": safe_float_conversion(data.get('RevenueTTM')),
            "return_on_equity": safe_float_conversion(data.get('ReturnOnEquityTTM')),
            "net_income": safe_float_conversion(income_statement_data),
            "total_assets": safe_float_conversion(balance_sheet_data.get("totalAssets")),
            "total_liabilities": safe_float_conversion(balance_sheet_data.get("totalLiabilities")),
            "total_shareholder_equity": safe_float_conversion(balance_sheet_data.get("totalShareholderEquity")),
            "total_current_assets": safe_float_conversion(balance_sheet_data.get("totalCurrentAssets")),
            "total_current_liabilities": safe_float_conversion(balance_sheet_data.get("totalCurrentLiabilities")),
            "long_term_debt": safe_float_conversion(balance_sheet_data.get("longTermDebt")),
            "cash_and_cash_equivalents": safe_float_conversion(
                balance_sheet_data.get("cashAndCashEquivalentsAtCarryingValue"))
        }

        stock_document = await StockFundamentalDataMongoDB.find_one(StockFundamentalDataMongoDB.symbol == symbol)

        if stock_document:
            logger.info(f"Updating existing document for {symbol}.")
            # Update existing document
            await stock_document.set(api_data)
        else:
            logger.info(f"No existing document for {symbol}, creating a new one.")
            # Create a new document from the dictionary
            stock_document = StockFundamentalDataMongoDB(**api_data)
            await stock_document.insert()

        await stock_document.save()
        logger.info(f"Successfully saved data for {symbol} to the database.")

        return stock_document

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during API request: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred for {symbol}: {e}")
        return None


async def fetch_balance_sheet(symbol: str) -> Optional[dict]:
    """Fetches the balance sheet data from Alpha Vantage."""
    params = {"function": "BALANCE_SHEET", "symbol": symbol, "apikey": API_KEY}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(MAIN_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if not data or "Error Message" in data:
            print(f"Error fetching BALANCE_SHEET for {symbol}: {data.get('Information', data)}")
            return None

        # Through None error if no annualReports found, using get with default empty list

        return_data = {
            "totalAssets": safe_float_conversion(data.get("annualReports", [{}])[0].get("totalAssets")),
            "totalLiabilities": safe_float_conversion(data.get("annualReports", [{}])[0].get("totalLiabilities")),
            "totalShareholderEquity": safe_float_conversion(data.get("annualReports", [{}])[0].get("totalShareholderEquity")),
            "totalCurrentAssets": safe_float_conversion(data.get("annualReports", [{}])[0].get("totalCurrentAssets")),
            "totalCurrentLiabilities": safe_float_conversion(data.get("annualReports", [{}])[0].get("totalCurrentLiabilities")),
            "longTermDebt": safe_float_conversion(data.get("annualReports", [{}])[0].get("longTermDebt")),
            "cashAndCashEquivalentsAtCarryingValue": safe_float_conversion(data.get("annualReports", [{}])[0].get("cashAndCashEquivalentsAtCarryingValue")),
        }
        return return_data
    except httpx.RequestError as e:
        print(f"HTTP error fetching BALANCE_SHEET for {symbol}: {e}")
        return None

async def fetch_income_statement(symbol: str) -> Optional[dict]:
    """Fetches the income statement data from Alpha Vantage."""
    params = {"function": "INCOME_STATEMENT", "symbol": symbol, "apikey": API_KEY}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(MAIN_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if not data or "Error Message" in data:
            print(f"Error fetching INCOME_STATEMENT for {symbol}: {data.get('Information', data)}")
            return None
        return_data = safe_float_conversion(data.get("annualReports", [{}])[0].get("netIncome"))
        return return_data
    except httpx.RequestError as e:
        print(f"HTTP error fetching INCOME_STATEMENT for {symbol}: {e}")
        return None

