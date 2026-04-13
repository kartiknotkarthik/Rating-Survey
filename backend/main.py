import sys
import os
import argparse
from Phase_1_Scraping.scrape_reviews import scrape_full_batch, save_phase_1_data
from Phase_2_Analysis.analyze_data import GrowwAnalyzerPhase2
from Phase_3_Email.send_email import GrowwMailerPhase3

def run_pipeline(receiver_email=None, recipient_name="Team"):
    print("--- STARTING GROWW PULSE PIPELINE ---")
    
    # Phase 1: Scraping
    print("\n[PHASE 1] Scraping & Filtering reviews...")
    df = scrape_full_batch(target_weeks=12, max_count=200)
    if df.empty:
        print("❌ No reviews found. Aborting.")
        return
    save_phase_1_data(df)
    
    # Phase 2: Analysis
    print("\n[PHASE 2] Analyzing reviews with Groq...")
    analyzer = GrowwAnalyzerPhase2()
    report, themes = analyzer.generate_pulse_report(df)
    
    # Save the report for Phase 3 access
    os.makedirs('reports', exist_ok=True)
    with open("reports/weekly_pulse_note.md", "w") as f:
        f.write(report)
        
    print(f"Analysis Complete! Identified themes: {', '.join(themes)}")
    
    # Optional JSON categorization
    df_copy = df.copy()
    df_copy['at'] = df_copy['at'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    categorized_json = analyzer.categorize_reviews_by_themes(df_copy, themes)
    with open("reports/themed_reviews.json", "w") as f:
        import json
        json.dump(categorized_json, f, indent=4)
    
    # Phase 3: Emailing
    print(f"\n[PHASE 3] Sending personalized email to {recipient_name}...")
    mailer = GrowwMailerPhase3()
    success, info = mailer.send_pulse_email(report, receiver_email=receiver_email, recipient_name=recipient_name)
    
    if success:
        print(f"SUCCESS! Weekly Pulse sent to {info['to']}")
    else:
        print(f"FAILED to send email: {info}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GROWW Pulse CLI Analyzer")
    parser.add_argument("--email", help="Recipient email address")
    parser.add_argument("--name", help="Recipient name", default="Team")
    
    args = parser.parse_args()
    
    run_pipeline(receiver_email=args.email, recipient_name=args.name)
