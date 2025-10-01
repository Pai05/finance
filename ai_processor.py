import google.generativeai as genai
import logging
import json

class AIProcessor:
    def __init__(self, api_key):
        """Initializes the AI Processor with the Gemini API key."""
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            logging.info("Gemini model 'gemini-1.5-flash-latest' initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to configure Gemini: {e}")
            raise

    def select_top_articles(self, articles, ticker):
        """Uses AI to select the top 5-7 most relevant articles."""
        if not articles:
            logging.warning("No articles provided for selection.")
            return []

        # Create a numbered list of articles for the prompt
        article_list_str = "\n".join([f"{i+1}. {article['title']} ({article['url']})" for i, article in enumerate(articles)])
        
        prompt = f"""
        Analyze the following financial news articles for the ticker "{ticker}".
        Select the top 5 to 7 most relevant, credible, and impactful articles that likely influenced today's market perception.
        Prioritize articles from reputable sources, those with specific data or earnings information, and analysis over generic market updates.

        Return your answer ONLY as a JSON object containing a single key "selected_urls", which is a list of the string URLs you have chosen. Do not include any other text, explanation, or markdown formatting.

        Example format:
        {{"selected_urls": ["https://url1.com/story", "https://url2.com/report"]}}

        Article List:
        {article_list_str}
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean the response to ensure it's valid JSON
            cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
            selected_data = json.loads(cleaned_response)
            selected_urls = selected_data.get("selected_urls", [])
            
            # Filter the original articles list to return full article objects
            top_articles = [article for article in articles if article['url'] in selected_urls]
            logging.info(f"AI selected {len(top_articles)} top articles for {ticker}.")
            return top_articles
        except Exception as e:
            logging.error(f"Error in AI article selection for {ticker}: {e}")
            # Fallback: return the first 5 articles if AI fails
            return articles[:5]

    def generate_summary(self, articles, history, ticker):
        """Generates a summary based on selected articles and historical context."""
        if not articles:
            logging.warning(f"No articles provided to generate summary for {ticker}.")
            return "No new significant articles were found to generate a summary today."

        article_context = "\n".join([f"- {article['title']}" for article in articles])
        history_context = "\n".join([f"Date: {date}\nSummary: {summary}\n---" for date, summary in history.items()])

        prompt = f"""
        You are a sharp, concise financial analyst. Your task is to provide a professional, data-driven summary for the stock ticker "{ticker}".

        Your summary must be under 500 words.

        **Historical Context (Summaries from the last 7 days):**
        {history_context if history else "No historical data available."}

        **Today's Key Articles:**
        {article_context}

        **Instructions:**
        1.  Synthesize the information from today's key articles.
        2.  Compare today's news with the historical context. Is this a new development, a continuation of a trend, or a contradiction of previous news?
        3.  Generate a comprehensive summary of the current situation.
        4.  Conclude with a mandatory section titled "**What changed today**" that explicitly highlights the single most important new development or piece of information from today's articles.

        Provide only the summary text. Do not include a title like "Summary for [TICKER]".
        """

        try:
            response = self.model.generate_content(prompt)
            logging.info(f"Successfully generated summary for {ticker}.")
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error in AI summary generation for {ticker}: {e}")
            return f"An error occurred during summary generation: {e}"