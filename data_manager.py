import json
import os
import pandas as pd
from datetime import datetime

DATA_FILE = "data/summaries.json"

def ensure_data_file():
    """Ensures the data directory and summaries.json file exist."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({}, f)

def load_data():
    """Loads all summary data from the JSON file."""
    ensure_data_file()
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_summary(ticker, summary, sources):
    """Saves a new summary for a given ticker, keeping a 7-day history."""
    all_data = load_data()
    if ticker not in all_data:
        all_data[ticker] = []

    # Get today's date in IST
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Remove any existing entry for today to prevent duplicates on re-run
    all_data[ticker] = [entry for entry in all_data[ticker] if entry['date'] != today_str]
    
    # Add the new summary
    new_entry = {
        'date': today_str,
        'summary': summary,
        'sources': sources
    }
    all_data[ticker].insert(0, new_entry)
    
    # Keep only the last 7 entries
    all_data[ticker] = all_data[ticker][:7]
    
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)

def get_summaries(ticker):
    """Retrieves all summaries for a specific ticker."""
    all_data = load_data()
    return all_data.get(ticker, [])

def get_ticker_list():
    """Gets a list of all tickers present in the data."""
    all_data = load_data()
    return sorted(list(all_data.keys()))