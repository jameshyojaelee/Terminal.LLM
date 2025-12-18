import yfinance as yf
import json

# Fetch just one ticker's news
spy = yf.Ticker("SPY")
news_list = spy.news

if news_list:
    print("--- RAW NEWS ITEM STRUCTURE ---")
    # Print the keys of the first news item
    first_item = news_list[0]
    print(json.dumps(first_item, indent=2)) 
else:
    print("No news found at all.")