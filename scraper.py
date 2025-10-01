import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Source 1: Finviz ---
def get_finviz_news(ticker):
    """Scrapes news headlines and URLs for a given ticker from Finviz."""
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    articles = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        news_table = soup.find(id='news-table')
        if not news_table:
            logging.warning(f"No news table found on Finviz for {ticker}.")
            return []
            
        for row in news_table.find_all('tr'):
            if row.a:
                title = row.a.get_text().strip()
                link = row.a['href']
                articles.append({'title': title, 'url': link, 'source': 'Finviz'})
        logging.info(f"Successfully scraped {len(articles)} articles from Finviz for {ticker}.")
        return articles
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Finviz page for {ticker}: {e}")
        return []

# --- Source 2: Polygon.io ---
def get_polygon_news(ticker, api_key):
    """Fetches news articles for a given ticker from the Polygon.io API."""
    url = f"https://api.polygon.io/v2/reference/news?ticker={ticker}&limit=15&apiKey={api_key}"
    articles = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for item in data.get('results', []):
            articles.append({
                'title': item.get('title'),
                'url': item.get('article_url'),
                'source': 'Polygon.io'
            })
        logging.info(f"Successfully fetched {len(articles)} articles from Polygon.io for {ticker}.")
        return articles
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Polygon.io news for {ticker}: {e}")
        return []

# --- Source 3: TradingView (using Playwright) ---
def get_tradingview_news(ticker):
    """Scrapes news headlines and URLs from TradingView's dynamic page."""
    url = f"https://www.tradingview.com/symbols/NYSE-{ticker}/news/"
    articles = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for the news container to be visible
            page.wait_for_selector('[class*="news-card-"]', timeout=15000)

            news_items = page.query_selector_all('[class*="news-card-"]')
            for item in news_items[:15]: # Limit to 15 articles
                title_element = item.query_selector('[class*="title-"]')
                link_element = item.query_selector('a[href]')
                if title_element and link_element:
                    title = title_element.inner_text().strip()
                    # TradingView links are relative, so we prepend the base URL
                    link = "https://www.tradingview.com" + link_element.get_attribute('href')
                    articles.append({'title': title, 'url': link, 'source': 'TradingView'})
            browser.close()
        logging.info(f"Successfully scraped {len(articles)} articles from TradingView for {ticker}.")
        return articles
    except Exception as e:
        logging.error(f"Error scraping TradingView for {ticker}: {e}")
        return []

# --- Main Aggregator Function ---
def get_all_news(ticker, polygon_api_key):
    """Aggregates news from all available sources for a given ticker."""
    logging.info(f"Starting news aggregation for ticker: {ticker}")
    
    # Run all scrapers
    finviz_news = get_finviz_news(ticker)
    polygon_news = get_polygon_news(ticker, polygon_api_key)
    tradingview_news = get_tradingview_news(ticker)
    
    # Combine and deduplicate articles based on URL
    all_articles = finviz_news + polygon_news + tradingview_news
    unique_articles = {article['url']: article for article in all_articles}.values()
    
    logging.info(f"Total unique articles found for {ticker}: {len(unique_articles)}")
    return list(unique_articles)