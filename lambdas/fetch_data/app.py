import yfinance as yf

def fetch_data_for_tickers(tickers):
    results = {}
    for ticker in tickers:
        t = yf.Ticker(ticker)
        
        # Store relevant data points for backtesting
        results[ticker] = {
            "history": t.history(period="1mo").to_dict(orient="records"),
            "dividends": t.dividends.to_dict(orient="records"),
            "splits": t.splits.to_dict(orient="records"),
            "actions": t.actions.to_dict(orient="records"),
            "earnings_dates": t.earnings_dates,
            "income_stmt": t.income_stmt.to_dict(orient="records"),
        }
        
    return results

def fetch_data(event, context):
    tickers = event.get('tickers', []).split(",") 

    if not tickers:
        raise ValueError("No tickers provided.")

    data = fetch_data_for_tickers(tickers)
    
    if not data:
        raise ValueError(f"Failed to fetch data for tickers: {tickers}")

    return data
