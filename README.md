Of course. Here is the complete README.md file. You can copy the entire block of text below and paste it directly into the README.md file on your GitHub repository.
AI Financial News Summarizer
This project is a web application that automatically gathers financial news for any stock ticker, uses AI to analyze it, and presents a professional, easy-to-read daily summary.

Multi-Source News Aggregation: Gathers news from Finviz, Polygon.io, and TradingView for comprehensive coverage.

AI-Powered Article Selection: Uses a Gemini AI model to intelligently select the top 5-7 most relevant articles from the aggregated list.

AI-Driven Daily Summaries: Generates a professional, concise summary of less than 500 words, including a "What changed today" section for quick insights.

Historical Context: Keeps a 7-day history of summaries for tracking trends.

Interactive UI: A clean, professional, and user-friendly interface built with Streamlit to view summaries by ticker.

Dynamic Ticker Management: Users can add new stock tickers to their watchlist directly from the UI.

Tech Stack & Architecture
Frontend: Streamlit

Backend & Scraping: Python

AI: Google Generative AI (Gemini)

Web Scraping: Playwright, Requests & BeautifulSoup4

Data Handling: Pandas

Deployment: Streamlit Community Cloud

The application operates on an on-demand basis. When a user clicks the "Refresh" button, the Streamlit backend triggers the scraping scripts. This data is then processed through a two-step AI pipeline to select articles and generate a summary, which is then saved and displayed.

Setup and Installation
Follow these steps to set up and run the project locally.

1. Prerequisites
Python (Version 3.11+ recommended)

Git

2. Clone the Repository
Bash

git clone https://github.com/Pai05/finance.git
cd finance
3. Install Dependencies
Install the required Python packages and the browser binaries for Playwright.

Bash

# Install Python libraries
pip install -r requirements.txt

# Install Playwright browsers
playwright install
4. Configure API Keys
The application requires API keys from Google and Polygon.io.

Create a file named secrets.toml inside a .streamlit folder (.streamlit/secrets.toml).

Add your keys to this file in the following format:

Ini, TOML

GOOGLE_API_KEY = "YOUR_GOOGLE_GEMINI_API_KEY"
POLYGON_API_KEY = "YOUR_POLYGON_IO_API_KEY"
Note: This secrets.toml file should not be committed to a public GitHub repository.

How to Run
Once the setup is complete, run the application from the project's root directory:

Bash

streamlit run app.py
The application will open in a new tab in your web browser.

Deployment
This application is designed for easy deployment on the Streamlit Community Cloud.

Push your project to a public GitHub repository.

Go to share.streamlit.io and link your GitHub account.

Select your repository and deploy.

Important: Add your API keys to the Streamlit Cloud secrets manager in the application's advanced settings.

Cost Analysis
This project is designed to be completely free to run and host.

Hosting: Deployed on the free tier of Streamlit Community Cloud.

AI Processing: Utilizes the generous free tier of the Gemini API.

Data APIs: Uses the free tier of the Polygon.io API.

Total Estimated Monthly Cost: $0.00