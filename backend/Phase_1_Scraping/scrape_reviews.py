import os
import pandas as pd
from google_play_scraper import reviews, Sort
from datetime import datetime, timedelta
import time
import re

def is_english_no_emoji(text):
    """
    Quality Filter:
    1. Removes emojis (keeps only ASCII)
    2. Minimum 5 words
    """
    # Remove non-ASCII (emojis, other scripts)
    ascii_only = re.sub(r'[^\x00-\x7F]+', '', text)
    # Filter by word count
    words = ascii_only.split()
    if len(words) < 5:
        return None
    return ascii_only.strip()

def scrape_full_batch(app_id='com.nextbillion.groww', target_weeks=12, max_count=200):
    cutoff_date = datetime.now() - timedelta(weeks=target_weeks)
    print(f"Starting Scraping: {app_id}")
    print(f"Target Cutoff: {cutoff_date.date()}")
    
    all_reviews = []
    continuation_token = None
    total_fetched = 0
    
    while total_fetched < max_count:
        try:
            result, continuation_token = reviews(
                app_id,
                lang='en',
                country='us',
                sort=Sort.NEWEST,
                count=100,
                continuation_token=continuation_token
            )
            
            if not result:
                break
                
            batch_count = 0
            reached_cutoff = False
            
            for r in result:
                if total_fetched + batch_count >= max_count:
                    break
                
                if r['at'] < cutoff_date:
                    reached_cutoff = True
                    break
                
                content = is_english_no_emoji(r['content'])
                if not content:
                    continue
                
                # Removing PII immediately (No title, no thumbsUpCount)
                all_reviews.append({
                    'reviewId': r['reviewId'],
                    'content': content,
                    'score': r['score'],
                    'at': r['at']
                })
                batch_count += 1
            
            total_fetched += batch_count
            print(f"Fetched batch: {batch_count} reviews (Total so far: {total_fetched})")
            
            if reached_cutoff or not continuation_token:
                print("Reached date cutoff or end of reviews.")
                break
                
            time.sleep(1)
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            break
            
    return pd.DataFrame(all_reviews)

def save_phase_1_data(df):
    os.makedirs('data', exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    csv_path = f"data/groww_reviews_{date_str}.csv"
    json_path = f"data/groww_reviews_{date_str}.json"
    
    df.to_csv(csv_path, index=False)
    df.to_json(json_path, orient='records', indent=4, date_format='iso')
    print(f"Data saved to {csv_path} and {json_path}")

if __name__ == "__main__":
    df = scrape_full_batch()
    if not df.empty:
        save_phase_1_data(df)
    else:
        print("No reviews found.")
