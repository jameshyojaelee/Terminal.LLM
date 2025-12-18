import yfinance as yf
from datetime import datetime, timezone
from typing import Optional

def get_market_data(watchlist):
    """
    Fetches LIVE price data and LIVE news via Yahoo Finance.
    Adapts to the 'content' nested JSON structure.
    """
    fetch_started_at = datetime.now(timezone.utc).astimezone()

    def iso_local(dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc).astimezone()
        else:
            dt = dt.astimezone()
        return dt.isoformat(timespec="seconds")

    # 1. Fetch Price Data (Real-time-ish)
    tickers = ["SPY", "QQQ", "BTC-USD"] + watchlist
    market_context = {}
    prices_as_of: Optional[datetime] = None
    
    try:
        # 'auto_adjust=True' is the new default, explicit is better
        data = yf.download(tickers, period="1d", group_by='ticker', progress=False, auto_adjust=True)
        
        for ticker in tickers:
            try:
                # Handle DataFrame extraction
                df = data[ticker]
                if df.empty:
                    market_context[ticker] = "N/A"
                    continue
                try:
                    last_ts = df.index[-1]
                    if hasattr(last_ts, "to_pydatetime"):
                        last_ts = last_ts.to_pydatetime()
                    if isinstance(last_ts, datetime):
                        if prices_as_of is None or last_ts > prices_as_of:
                            prices_as_of = last_ts
                except Exception:
                    pass

                # Calculate % Change
                current_price = df['Close'].iloc[-1]
                open_price = df['Open'].iloc[0]
                change = ((current_price - open_price) / open_price) * 100
                
                market_context[ticker] = f"{change:+.2f}%"
            except Exception:
                market_context[ticker] = "0.00%"
    except Exception as e:
        print(f"Error fetching prices: {e}")

    # 2. Fetch News (Parsed Correctly)
    headlines = []
    news_as_of: Optional[datetime] = None
    
    # Helper function to extract title safely
    def extract_news(ticker_symbol, prefix):
        nonlocal news_as_of
        try:
            stock = yf.Ticker(ticker_symbol)
            news_list = stock.news
            # Get top 2 stories
            for item in news_list[:2]:
                # THE FIX: Check inside 'content' dictionary
                content = item.get('content', {})
                title = content.get('title')

                publish_ts = (
                    content.get("pubDate")
                    or item.get("providerPublishTime")
                    or content.get("providerPublishTime")
                )
                # providerPublishTime is typically epoch seconds
                try:
                    if isinstance(publish_ts, (int, float)):
                        dt = datetime.fromtimestamp(publish_ts, tz=timezone.utc).astimezone()
                        if news_as_of is None or dt > news_as_of:
                            news_as_of = dt
                except Exception:
                    pass
                
                # Fallback if structure varies
                if not title:
                    title = item.get('title', 'No Title')
                
                if title != 'No Title':
                    headlines.append(f"{prefix}: {title}")
        except Exception:
            pass

    # Get Macro News (SPY)
    extract_news("SPY", "MACRO")

    # Get Watchlist News
    for ticker in watchlist:
        extract_news(ticker, ticker)

    # 3. Assemble Output
    fetch_finished_at = datetime.now(timezone.utc).astimezone()
    return {
        "date": fetch_finished_at.strftime("%Y-%m-%d %H:%M:%S %z"),
        "retrieved_at": iso_local(fetch_finished_at),
        "retrieval_window": {
            "started_at": iso_local(fetch_started_at),
            "finished_at": iso_local(fetch_finished_at),
        },
        "source_as_of": {
            "prices_as_of": iso_local(prices_as_of),
            "news_as_of": iso_local(news_as_of),
        },
        "user_profile": {"watchlist": watchlist},
        "market_context": market_context,
        "headlines": headlines
    }
