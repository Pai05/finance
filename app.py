import streamlit as st
import os

# Import our custom modules
from scraper import get_all_news
from ai_processor import AIProcessor
import data_manager

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="AI Financial News Summarizer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a professional look ---
def load_css():
    st.markdown("""
        <style>
            /* --- Import a clean font from Google Fonts --- */
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            
            html, body, [class*="st-"] {
                font-family: 'Roboto', sans-serif;
            }

            /* --- Main container styling --- */
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
            .st-emotion-cache-1y4p8pa {
                border-radius: 0.5rem;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: 1px solid #e6e6e6;
            }

            /* --- Sidebar Styling --- */
            [data-testid="stSidebar"] {
                background-color: #0c59c5; /* A slightly darker blue for the sidebar */
            }
             [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
                color: #ffffff; /* White text in sidebar */
            }

            /* --- Button Styles --- */
            .stButton>button {
                border-radius: 0.5rem;
                border: none;
                background-color: #0d6efd; /* Use primary color */
                color: white;
                font-weight: 700;
                padding: 0.75rem 1.5rem;
                transition: all 0.2s ease-in-out;
                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
            }
            .stButton>button:hover {
                background-color: #0b5ed7; /* A slightly darker blue on hover */
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                transform: translateY(-2px); /* Slight lift effect */
            }
             .stButton>button:active {
                background-color: #0a58ca;
                transform: translateY(0);
            }

            /* --- Tab Styles --- */
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                background-color: transparent;
                padding-left: 0;
                padding-right: 0;
            }
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                font-size: 1.1rem;
            }
            .stTabs [data-baseweb="tab--selected"] {
                color: #0d6efd;
                border-bottom: 3px solid #0d6efd;
            }

        </style>
    """, unsafe_allow_html=True)

# --- Load all assets ---
load_css()

# --- Initialize AI and API Keys ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    POLYGON_API_KEY = st.secrets["POLYGON_API_KEY"]
    ai_processor = AIProcessor(api_key=GOOGLE_API_KEY)
except Exception:
    st.error("API keys not found. Please add them to your .streamlit/secrets.toml file.")
    st.stop()

# --- Caching Data ---
@st.cache_data(ttl=3600)
def get_cached_summaries(ticker):
    return data_manager.get_summaries(ticker)

@st.cache_data(ttl=3600)
def get_cached_ticker_list():
    return data_manager.get_ticker_list()

# --- Sidebar for Ticker Management ---
with st.sidebar:
    st.title("📈 Finance Feed AI")
    st.markdown("Your intelligent news summarizer.")
    
    if 'tickers' not in st.session_state:
        st.session_state.tickers = get_cached_ticker_list()
        if not st.session_state.tickers:
            st.session_state.tickers = ["AAPL", "GOOGL", "MSFT"]

    selected_ticker = st.radio(
        "Select a Ticker",
        st.session_state.tickers,
        key="selected_ticker"
    )

    st.markdown("---")
    new_ticker = st.text_input("Add New Ticker", placeholder="e.g., NVDA").upper()
    if st.button("Add Ticker"):
        if new_ticker and new_ticker not in st.session_state.tickers:
            st.session_state.tickers.append(new_ticker)
            st.success(f"Added {new_ticker}")
            st.rerun()
        else:
            st.warning("Please enter a valid, unique ticker.")

# --- Main Content Area ---
if selected_ticker:
    # --- Header with Refresh Button ---
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header(f"News Summary for ${selected_ticker}")
    with col2:
        if st.button(f"🔄 Refresh News for {selected_ticker}", use_container_width=True):
            with st.spinner("Fetching and summarizing news... This may take a moment."):
                all_articles = get_all_news(selected_ticker, POLYGON_API_KEY)
                if all_articles:
                    top_articles = ai_processor.select_top_articles(all_articles, selected_ticker)
                    historical_summaries = get_cached_summaries(selected_ticker)
                    history_for_prompt = {item['date']: item['summary'] for item in historical_summaries[1:7]}
                    new_summary = ai_processor.generate_summary(top_articles, history_for_prompt, selected_ticker)
                    data_manager.save_summary(selected_ticker, new_summary, top_articles)
                    st.cache_data.clear()
                    st.success("Summary updated successfully!")
                    st.rerun()
                else:
                    st.warning("Could not find any recent articles.")

    # --- Display Summaries using Tabs ---
    summaries = get_cached_summaries(selected_ticker)
    if not summaries:
        st.info(f"No summaries found. Click 'Refresh' to generate one.")
    else:
        latest_summary = summaries[0]
        
        tab1, tab2, tab3 = st.tabs(["Today's Summary", "Sources", "Historical Data"])

        with tab1:
            st.subheader(f"Summary for {latest_summary['date']}")
            st.markdown(latest_summary['summary'])

        with tab2:
            st.subheader("Sources Used for Today's Summary")
            if latest_summary['sources']:
                for source in latest_summary['sources']:
                    st.markdown(f"- **[{source['title']}]({source['url']})** via *{source['source']}*")
            else:
                st.write("No sources were used for this summary.")
        
        with tab3:
            st.subheader("Past Summaries")
            if len(summaries) > 1:
                for item in summaries[1:]:
                    with st.expander(f"🗓️ {item['date']}"):
                        st.markdown(item['summary'])
            else:
                st.info("No older summaries available.")

else:
    st.info("Please add and select a ticker from the sidebar to begin.")