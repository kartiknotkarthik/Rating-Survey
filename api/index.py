from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add current and root directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from backend.Phase_1_Scraping.scrape_reviews import scrape_full_batch
from backend.Phase_2_Analysis.analyze_data import GrowwAnalyzerPhase2
from backend.Phase_3_Email.send_email import GrowwMailerPhase3

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        request_body = json.loads(post_data.decode('utf-8'))
        
        name = request_body.get('name', 'Team Member')
        email = request_body.get('email')
        
        if not email:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Email is required"}).encode('utf-8'))
            return

        try:
            # 1. Scrape
            reviews_list = scrape_full_batch(max_count=200)
            
            # 2. Analyze
            analyzer = GrowwAnalyzerPhase2()
            report, themes = analyzer.generate_pulse_report(reviews_list)
            
            # 3. Mail
            mailer = GrowwMailerPhase3()
            success, info = mailer.send_pulse_email(report, receiver_email=email, recipient_name=name)
            
            if success:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "Pulse generated and sent successfully"}).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": f"Email failed: {info}"}).encode('utf-8'))
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": f"Internal Error: {str(e)}"}).encode('utf-8'))
            
    def do_GET(self):
        # Trigger point for Vercel Cron
        try:
            email = os.getenv("RECEIVER_EMAIL")
            name = "Stakeholder"
            
            # 1. Scrape
            reviews_list = scrape_full_batch(max_count=100) # Speed it up for Cron
            
            # 2. Analyze
            analyzer = GrowwAnalyzerPhase2()
            report, themes = analyzer.generate_pulse_report(reviews_list)
            
            # 3. Mail
            mailer = GrowwMailerPhase3()
            success, info = mailer.send_pulse_email(report, receiver_email=email, recipient_name=name)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Weekly Cron Pulse Triggered", "success": success}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": f"Cron Error: {str(e)}"}).encode('utf-8'))
