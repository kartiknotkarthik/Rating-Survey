import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load API keys from root .env
# Load API keys from root .env
# Phase_2_Analysis is at backend/Phase_2_Analysis/
# Root is 3 levels up from this FILE
file_path = os.path.abspath(__file__)
root_path = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
dotenv_path = os.path.join(root_path, ".env")
load_dotenv(dotenv_path=dotenv_path)

class GrowwAnalyzerPhase2:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment. Please check your .env file.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.1-8b-instant"

    def _get_llm_response(self, system_prompt, user_prompt):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                temperature=0.1,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error communicating with Groq: {e}"

    def extract_themes(self, reviews_text):
        system_prompt = "You are a Senior Product Manager at GROWW. Identify EXACTLY 5 high-level recurring themes from user feedback."
        user_prompt = f"""
        Analyze these GROWW user reviews and extract EXACTLY 5 the most prominent themes.
        Respond ONLY with the theme names separated by commas.
        
        REVIEWS:
        {reviews_text}
        """
        themes_raw = self._get_llm_response(system_prompt, user_prompt)
        return [t.strip() for t in themes_raw.split(',') if t.strip()][:5]

    def categorize_reviews_by_themes(self, reviews_list, themes):
        """
        Categorizes each review into one of the identified themes.
        """
        categorized_data = {theme: [] for theme in themes}
        categorized_data["Uncategorized"] = []
        
        batch_size = 10
        for i in range(0, len(reviews_list), batch_size):
            batch = reviews_list[i:i+batch_size]
            batch_text = "\n".join([f"ID: {r['reviewId']} | Content: {r['content']}" for r in batch])
            
            prompt = f"""
            Categorize each of these GROWW reviews into EXACTLY ONE of the following themes: {', '.join(themes)}.
            If none fit well, use 'Uncategorized'.
            
            REVIEWS:
            {batch_text}
            
            Respond ONLY with a JSON list of objects: [{{"id": "...", "theme": "..."}}, ...]
            """
            
            response = self._get_llm_response("You are a data categorization assistant.", prompt)
            try:
                json_str = response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:-3].strip()
                elif json_str.startswith("```"):
                    json_str = json_str[3:-3].strip()
                    
                results = json.loads(json_str)
                for res in results:
                    matching_review = next((r for r in batch if r['reviewId'] == res['id']), None)
                    if matching_review:
                        theme_key = res['theme'] if res['theme'] in categorized_data else "Uncategorized"
                        categorized_data[theme_key].append(matching_review)
            except Exception:
                for r in batch:
                    categorized_data["Uncategorized"].append(r)
                    
        return categorized_data

    def generate_pulse_report(self, reviews_list):
        sample = reviews_list[:100]
        reviews_block = "\n".join([f"- [Rating: {r['score']}] {r['content']}" for r in sample])
        
        themes = self.extract_themes(reviews_block[:4000])
        
        system_prompt = f"""
        You are a Product Analyst for GROWW. Generate a 'Weekly Pulse' one-page note.
        Themes to focus on: {', '.join(themes)}
        """
        
        user_prompt = f"""
        Based on the reviews below, provide:
        1. Top 3 Themes: Summarize what users are saying for each.
        2. 3 Real User Quotes: Select representative, impactful quotes (No PII).
        3. 3 Action Ideas: Strategic or tactical fixes for the Groww team.
        
        REVIEWS DATA:
        {reviews_block}
        
        Format as professional Markdown.
        """
        
        report = self._get_llm_response(system_prompt, user_prompt)
        return report, themes
