import os
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# Load API keys from root .env
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_path, ".env")
load_dotenv(dotenv_path=dotenv_path)

class GrowwAnalyzerPhase2:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment. Please check your .env file.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

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

    def categorize_reviews_by_themes(self, df, themes):
        """
        Categorizes each review into one of the identified themes.
        """
        categorized_data = {theme: [] for theme in themes}
        categorized_data["Uncategorized"] = []
        
        # To avoid too many API calls, we'll process in batches of 10
        batch_size = 10
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            reviews_list = "\n".join([f"ID: {r['reviewId']} | Content: {r['content']}" for _, r in batch.iterrows()])
            
            prompt = f"""
            Categorize each of these GROWW reviews into EXACTLY ONE of the following themes: {', '.join(themes)}.
            If none fit well, use 'Uncategorized'.
            
            REVIEWS:
            {reviews_list}
            
            Respond ONLY with a JSON list of objects: [{{"id": "...", "theme": "..."}}, ...]
            """
            
            response = self._get_llm_response("You are a data categorization assistant.", prompt)
            try:
                # Clean response if LLM adds markdown backticks
                json_str = response.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:-3].strip()
                elif json_str.startswith("```"):
                    json_str = json_str[3:-3].strip()
                    
                results = json.loads(json_str)
                for res in results:
                    matching_review = df[df['reviewId'] == res['id']].iloc[0].to_dict()
                    theme_key = res['theme'] if res['theme'] in categorized_data else "Uncategorized"
                    categorized_data[theme_key].append(matching_review)
            except Exception as e:
                print(f"Error parsing categorization for batch {i}: {e}")
                for _, r in batch.iterrows():
                    categorized_data["Uncategorized"].append(r.to_dict())
                    
        return categorized_data

    def generate_pulse_report(self, df):
        sample_df = df.head(100) 
        reviews_block = "\n".join([f"- [Rating: {r['score']}] {r['content']}" for _, r in sample_df.iterrows()])
        
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

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    if not os.path.exists(data_dir):
        print("Data directory not found. Please run Phase 1 first.")
    else:
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        if not json_files:
            print("No JSON data found in ../data. Run Phase 1 first.")
        else:
            latest_file = os.path.join(data_dir, sorted(json_files)[-1])
            print(f"Reading latest data: {latest_file}")
            
            with open(latest_file, 'r') as f:
                data = json.load(f)
                df = pd.DataFrame(data)
            
            analyzer = GrowwAnalyzerPhase2()
            print("Analyzing reviews and generating report...")
            report, themes = analyzer.generate_pulse_report(df)
            
            # Save report
            os.makedirs('reports', exist_ok=True)
            with open("reports/weekly_pulse_note.md", "w") as f:
                f.write(report)
            
            print("Categorizing all reviews by themes (this may take a moment)...")
            categorized_json = analyzer.categorize_reviews_by_themes(df, themes)
            
            with open("reports/themed_reviews.json", "w") as f:
                json.dump(categorized_json, f, indent=4)
                
            print(f"Success! \n- Report: reports/weekly_pulse_note.md\n- Grouped JSON: reports/themed_reviews.json")
