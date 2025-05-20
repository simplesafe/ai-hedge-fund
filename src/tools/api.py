import datetime
import os
import pandas as pd
import yfinance as yf
from typing import Optional

from src.data.cache import get_cache
from src.data.models import (
    CompanyNews,
    CompanyNewsResponse,
    FinancialMetrics,
    FinancialMetricsResponse,
    Price,
    PriceResponse,
    LineItem,
    LineItemResponse,
    InsiderTrade,
    InsiderTradeResponse,
    CompanyFactsResponse,
)

# Global cache instance
_cache = get_cache()


def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    """Fetch price data from cache or Yahoo Finance."""
    # Check cache first
    if cached_data := _cache.get_prices(ticker):
        # Filter cached data by date range and convert to Price objects
        filtered_data = [Price(**price) for price in cached_data if start_date <= price["time"] <= end_date]
        if filtered_data:
            return filtered_data

    # If not in cache or no data in range, fetch from Yahoo Finance
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            return []

        # Convert DataFrame to list of Price objects
        prices = []
        for index, row in df.iterrows():
            price = Price(
                open=float(row['Open']),
                close=float(row['Close']),
                high=float(row['High']),
                low=float(row['Low']),
                volume=int(row['Volume']),
                time=index.strftime('%Y-%m-%d')
            )
            prices.append(price)

        # Cache the results
        _cache.set_prices(ticker, [p.model_dump() for p in prices])
        return prices
    except Exception as e:
        raise Exception(f"Error fetching data from Yahoo Finance: {ticker} - {str(e)}")


def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[FinancialMetrics]:
    """Fetch financial metrics from cache or Yahoo Finance."""
    # Check cache first
    if cached_data := _cache.get_financial_metrics(ticker):
        # Filter cached data by date and limit
        filtered_data = [FinancialMetrics(**metric) for metric in cached_data if metric["report_period"] <= end_date]
        filtered_data.sort(key=lambda x: x.report_period, reverse=True)
        if filtered_data:
            return filtered_data[:limit]

    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Create FinancialMetrics object from Yahoo Finance data
        metrics = FinancialMetrics(
            ticker=ticker,
            report_period=end_date,
            period=period,
            currency=info.get('currency', 'USD'),
            market_cap=info.get('marketCap'),
            enterprise_value=info.get('enterpriseValue'),
            price_to_earnings_ratio=info.get('trailingPE'),
            price_to_book_ratio=info.get('priceToBook'),
            price_to_sales_ratio=info.get('priceToSalesTrailing12Months'),
            enterprise_value_to_ebitda_ratio=info.get('enterpriseToEbitda'),
            enterprise_value_to_revenue_ratio=info.get('enterpriseToRevenue'),
            free_cash_flow_yield=info.get('freeCashflowYield'),
            peg_ratio=info.get('pegRatio'),
            gross_margin=info.get('grossMargins'),
            operating_margin=info.get('operatingMargins'),
            net_margin=info.get('profitMargins'),
            return_on_equity=info.get('returnOnEquity'),
            return_on_assets=info.get('returnOnAssets'),
            return_on_invested_capital=info.get('returnOnInvestedCapital'),
            asset_turnover=info.get('assetTurnover'),
            inventory_turnover=info.get('inventoryTurnover'),
            receivables_turnover=info.get('receivablesTurnover'),
            days_sales_outstanding=info.get('daysSalesOutstanding'),
            operating_cycle=info.get('operatingCycle'),
            working_capital_turnover=info.get('workingCapitalTurnover'),
            current_ratio=info.get('currentRatio'),
            quick_ratio=info.get('quickRatio'),
            cash_ratio=info.get('cashRatio'),
            operating_cash_flow_ratio=info.get('operatingCashflowRatio'),
            debt_to_equity=info.get('debtToEquity'),
            debt_to_assets=info.get('debtToAssets'),
            interest_coverage=info.get('interestCoverage'),
            revenue_growth=info.get('revenueGrowth'),
            earnings_growth=info.get('earningsGrowth'),
            book_value_growth=info.get('bookValueGrowth'),
            earnings_per_share_growth=info.get('earningsQuarterlyGrowth'),
            free_cash_flow_growth=info.get('freeCashflowGrowth'),
            operating_income_growth=info.get('operatingIncomeGrowth'),
            ebitda_growth=info.get('ebitdaGrowth'),
            payout_ratio=info.get('payoutRatio'),
            earnings_per_share=info.get('trailingEps'),
            book_value_per_share=info.get('bookValue'),
            free_cash_flow_per_share=info.get('freeCashflowPerShare')
        )

        # Cache the results
        _cache.set_financial_metrics(ticker, [metrics.model_dump()])
        return [metrics]
    except Exception as e:
        raise Exception(f"Error fetching financial metrics from Yahoo Finance: {ticker} - {str(e)}")


def get_company_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[CompanyNews]:
    """Fetch company news from cache or Yahoo Finance."""
    # Check cache first
    if cached_data := _cache.get_company_news(ticker):
        # Filter cached data by date range
        filtered_data = [CompanyNews(**news) for news in cached_data if (start_date is None or news["date"] >= start_date) and news["date"] <= end_date]
        filtered_data.sort(key=lambda x: x.date, reverse=True)
        if filtered_data:
            return filtered_data

    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            return []

        # Convert news to CompanyNews objects
        company_news = []
        for item in news:
            if start_date and item.get('providerPublishTime', 0) < pd.Timestamp(start_date).timestamp() * 1000:
                continue
            if item.get('providerPublishTime', 0) > pd.Timestamp(end_date).timestamp() * 1000:
                continue
                
            news_item = CompanyNews(
                ticker=ticker,
                title=item.get('title', ''),
                author=item.get('publisher', ''),
                source=item.get('publisher', ''),
                date=pd.Timestamp(item.get('providerPublishTime', 0), unit='ms').strftime('%Y-%m-%d'),
                url=item.get('link', ''),
                sentiment=None  # Yahoo Finance doesn't provide sentiment
            )
            company_news.append(news_item)
            
            if len(company_news) >= limit:
                break

        # Cache the results
        _cache.set_company_news(ticker, [news.model_dump() for news in company_news])
        return company_news
    except Exception as e:
        raise Exception(f"Error fetching news from Yahoo Finance: {ticker} - {str(e)}")


def get_company_facts(ticker: str) -> CompanyFactsResponse:
    """Fetch company facts from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        facts = CompanyFacts(
            ticker=ticker,
            name=info.get('longName', ''),
            cik=info.get('cik'),
            industry=info.get('industry'),
            sector=info.get('sector'),
            category=info.get('category'),
            exchange=info.get('exchange'),
            is_active=True,  # Yahoo Finance only shows active companies
            listing_date=info.get('firstTradeDateEpochUtc'),
            location=info.get('country'),
            market_cap=info.get('marketCap'),
            number_of_employees=info.get('fullTimeEmployees'),
            sec_filings_url=info.get('secFilingsUrl'),
            sic_code=info.get('sicCode'),
            sic_industry=info.get('industry'),
            sic_sector=info.get('sector'),
            website_url=info.get('website'),
            weighted_average_shares=info.get('sharesOutstanding')
        )
        
        return CompanyFactsResponse(company_facts=facts)
    except Exception as e:
        raise Exception(f"Error fetching company facts from Yahoo Finance: {ticker} - {str(e)}")


# Note: Yahoo Finance doesn't provide insider trading data
def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[InsiderTrade]:
    """This function is not supported with Yahoo Finance."""
    return []


def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[LineItem]:
    """This function is not supported with Yahoo Finance."""
    return []


def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    """Convert list of Price objects to DataFrame."""
    if not prices:
        return pd.DataFrame()
    
    data = {
        'open': [p.open for p in prices],
        'high': [p.high for p in prices],
        'low': [p.low for p in prices],
        'close': [p.close for p in prices],
        'volume': [p.volume for p in prices]
    }
    
    df = pd.DataFrame(data, index=pd.to_datetime([p.time for p in prices]))
    return df


def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Get price data as DataFrame."""
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)


def get_market_cap(
    ticker: str,
    end_date: str,
) -> float | None:
    """Fetch market cap from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('marketCap')
    except Exception as e:
        print(f"Error fetching market cap from Yahoo Finance: {ticker} - {str(e)}")
        return None
