import streamlit as st
from datetime import datetime
import os

# Import our custom modules
from scraper import get_all_news
from ai_processor import AIProcessor
import data_manager

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Financial News Summarizer",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI Financial News Summarizer")
st.markdown("An intelligent tool to get concise, AI-powered daily news summaries for your stocks.")

# --- Initialize AI and API Keys ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    POLYGON_API_KEY = st.secrets["POLYGON_API_KEY"]
    ai_processor = AIProcessor(api_key=GOOGLE_API_KEY)
except KeyError:
    st.error("API keys not found. Please add GOOGLE_API_KEY and POLYGON_API_KEY to your .streamlit/secrets.toml file.")
    st.stop()
except Exception as e:
    st.error(f"Failed to initialize the AI Processor: {e}")
    st.stop()


# --- Caching Data ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def get_cached_summaries(ticker):
    return data_manager.get_summaries(ticker)

@st.cache_data(ttl=3600)
def get_cached_ticker_list():
    return data_manager.get_ticker_list()

# --- Sidebar for Ticker Management ---
with st.sidebar:
    st.header("Manage Tickers")
    
    # Initialize session state for tickers
    if 'tickers' not in st.session_state:
        st.session_state.tickers = get_cached_ticker_list()
        # Add a default ticker if list is empty for first-time users
        if not st.session_state.tickers:
            st.session_state.tickers = ["AAPL", "GOOGL", "MSFT"]

    # Ticker selection
    selected_ticker = st.radio(
        "Select a Ticker",
        st.session_state.tickers,
        key="selected_ticker"
    )

    st.markdown("---")

    # Add new ticker
    new_ticker = st.text_input("Add New Ticker (e.g., NVDA)").upper()
    if st.button("Add Ticker"):
        if new_ticker and new_ticker not in st.session_state.tickers:
            st.session_state.tickers.append(new_ticker)
            st.success(f"Added {new_ticker}")
            st.rerun()
        elif not new_ticker:
            st.warning("Please enter a ticker symbol.")
        else:
            st.info(f"{new_ticker} is already in the list.")

# --- Main Content Area ---
if selected_ticker:
    st.header(f"News Summary for ${selected_ticker}")

    # --- Refresh Button Logic ---
    if st.button(f"🔄 Refresh News for {selected_ticker}"):
        with st.spinner(f"Fetching and summarizing news for {selected_ticker}... This may take a moment."):
            try:
                # 1. Scrape data
                all_articles = get_all_news(selected_ticker, POLYGON_API_KEY)
                
                if not all_articles:
                    st.warning("Could not find any recent articles for this ticker.")
                else:
                    # 2. AI selects top articles
                    top_articles = ai_processor.select_top_articles(all_articles, selected_ticker)

                    # 3. Get historical context (last 6 days)
                    historical_summaries = get_cached_summaries(selected_ticker)
                    history_for_prompt = {item['date']: item['summary'] for item in historical_summaries[1:7]}

                    # 4. AI generates summary
                    new_summary = ai_processor.generate_summary(top_articles, history_for_prompt, selected_ticker)
                    
                    # 5. Save the new summary
                    data_manager.save_summary(selected_ticker, new_summary, top_articles)
                    
                    # Clear cache to load the new data
                    st.cache_data.clear()
                    st.success(f"Summary for {selected_ticker} updated successfully!")
                    st.rerun()

            except Exception as e:
                st.error(f"An error occurred during the refresh process: {e}")

    # --- Display Summaries ---
    summaries = get_cached_summaries(selected_ticker)

    if not summaries:
        st.info(f"No summaries found for {selected_ticker}. Click the 'Refresh' button to generate one.")
    else:
        # Display today's summary prominently
        latest_summary = summaries[0]
        st.subheader(f"Summary for {latest_summary['date']}")
        st.markdown(latest_summary['summary'])

        with st.expander("Show Sources Used for Today's Summary"):
            if latest_summary['sources']:
                for source in latest_summary['sources']:
                    st.markdown(f"- **[{source['title']}]({source['url']})** via *{source['source']}*")
            else:
                st.write("No specific sources were used for this summary.")

        st.markdown("---")

        # Display historical summaries
        st.subheader("Historical Summaries (Last 7 Days)")
        if len(summaries) > 1:
            for item in summaries[1:]:
                with st.expander(f"🗓️ {item['date']}"):
                    st.markdown(item['summary'])
        else:
            st.write("No older summaries available.")

else:
    st.info("Add and select a ticker from the sidebar to begin.")