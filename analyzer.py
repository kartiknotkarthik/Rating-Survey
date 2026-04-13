import os
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GrowwAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3-70b-8192"

    def _get_llm_response(self, prompt):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional Product Analyst at GROWW, an investment platform. Your task is to analyze user reviews and extract high-level strategic insights. Be concise, objective, and action-oriented."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content

    def generate_themes(self, reviews_list):
        """
        Takes a list of review texts and returns 3-5 themes.
        """
        # Truncate content if too long for initial theme extraction
        combined_text = "\n".join([f"- {r}" for r in reviews_list[:100]]) # Sample first 100 for theme discovery
        
        prompt = f"""
        Analyze the following user reviews for the GROWW app and identify the 3 to 5 most prominent themes or categories they fall into.
        
        Reviews:
        {combined_text}
        
        Respond ONLY with the names of the 3-5 themes, separated by commas.
        """
        
        themes_raw = self._get_llm_response(prompt)
        themes = [t.strip() for t in themes_raw.split(',')]
        return themes[:5]

    def analyze_weekly_pulse(self, df):
        """
        Generates the full weekly pulse note.
        """
        if df.empty:
            return "No reviews found for the specified period."

        # Prepare review data for analysis
        # We'll prioritize reviews with content and maybe low ratings for 'action ideas'
        # Or just a representative sample
        sample_reviews = df.sort_values(by='thumbsUpCount', ascending=False).head(50)
        review_texts = sample_reviews['content'].tolist()
        
        themes = self.generate_themes(review_texts)
        
        reviews_summary = "\n".join([f"- [Rating: {r['score']}*] {r['content']}" for _, r in sample_reviews.iterrows()])
        
        prompt = f"""
        Based on the following reviews for GROWW, generate a 'Weekly Pulse' report.
        
        THEMES IDENTIFIED: {', '.join(themes)}
        
        REVIEWS DATA:
        {reviews_summary}
        
        The report must include:
        1. **Top 3 Themes**: Explain what users are saying about these specifically.
        2. **3 Real User Quotes**: Pick 3 impactful quotes that represent the sentiment (ensure PII is removed).
        3. **3 Action Ideas**: Practical steps for the product/tech team to address the feedback.
        
        Format the output as a clean, professional markdown report suitable for an internal email.
        """
        
        pulse_report = self._get_llm_response(prompt)
        return pulse_report

if __name__ == "__main__":
    # Test with mockup data if CSV doesn't exist
    analyzer = GrowwAnalyzer()
    if os.path.exists('data/reviews_raw.csv'):
        df = pd.read_csv('data/reviews_raw.csv')
        report = analyzer.analyze_weekly_pulse(df)
        print(report)
        with open('data/weekly_pulse.md', 'w') as f:
            f.write(report)
    else:
        print("Scraper data not found. Run scraper.py first.")
