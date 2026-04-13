from google_play_scraper import reviews, Sort
import pandas as pd
from datetime import datetime, timedelta
import time
import re

def is_english_no_emoji(text):
    """
    Checks if text is primarily English (Latin characters, common punctuation)
    and contains NO emojis.
    """
    clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
    if len(clean_text) < len(text):
        return False
    return True

def fetch_groww_reviews(weeks=8, max_count=200, app_id='com.nextbillion.groww'):
    """
    Robust fetcher used by the Main App. 
    Correctly handles pagination to exceed the 200-review limit.
    """
    cutoff_date = datetime.now() - timedelta(weeks=weeks)
    all_reviews = []
    continuation_token = None
    
    while len(all_reviews) < max_count:
        batch, continuation_token = reviews(
            app_id,
            lang='en',
            country='in',
            sort=Sort.NEWEST,
            count=100,
            continuation_token=continuation_token
        )
        
        if not batch:
            break
            
        should_stop = False
        for r in batch:
            if r['at'] < cutoff_date:
                should_stop = True
                break
            
            content = r['content'] if r['content'] else ""
            word_count = len(content.split())
            
            # Filter: Only keep reviews with 5 or more words
            if word_count < 5:
                continue
            
            # Filter: Pure English, No Emojis
            if not is_english_no_emoji(content):
                continue

            # Clean data (PII Stripping - No title, no thumbsUpCount)
            all_reviews.append({
                'reviewId': r['reviewId'],
                'content': content,
                'at': r['at'],
                'score': r['score']
            })
            
        if should_stop or not continuation_token:
            break
        
        # Respectful throttle
        time.sleep(0.5)
            
    df = pd.DataFrame(all_reviews)
    if not df.empty:
        df.drop_duplicates(subset=['reviewId'], inplace=True)
        df.sort_values(by='at', ascending=False, inplace=True)
        
    return df
