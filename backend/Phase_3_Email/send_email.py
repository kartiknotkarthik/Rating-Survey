import os
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai
from dotenv import load_dotenv

# Load credentials from root .env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)

# Configure Gemini
google_api_key = os.getenv("GOOGLE_API_KEY")
if google_api_key:
    genai.configure(api_key=google_api_key)

class GrowwMailerPhase3:
    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.receiver_email = os.getenv("RECEIVER_EMAIL")
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        
    def generate_email_context(self, report_content):
        if not google_api_key:
            return "GROWW Weekly Pulse Report", ""
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"Analyze this report and provide: 1. Subject line. 2. 2-sentence executive summary. Respond in JSON: {{\"subject\": \"...\", \"intro\": \"...\"}}\n\nREPORT:\n{report_content[:3000]}"
            response = model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            return data.get("subject", "GROWW Weekly Pulse"), data.get("intro", "")
        except Exception:
            return "GROWW Weekly Pulse Report", ""

    def send_via_resend(self, to_email, subject, body):
        """Transaction API for Vercel Compatibility"""
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.resend_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "from": "Groww Pulse <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "text": body
        }
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200, response.text

    def send_pulse_email(self, report_md, receiver_email=None, recipient_name="Team"):
        target_email = receiver_email if receiver_email else self.receiver_email
        if not target_email:
            return False, "No recipient email provided."

        subject, intro = self.generate_email_context(report_md)
        greeting = f"Hi {recipient_name}!\n\n"
        email_body = f"{greeting}{intro}\n\n---\n\n{report_md}"

        # OPTION 1: Use Resend API (Preferred for Vercel)
        if self.resend_api_key:
            success, msg = self.send_via_resend(target_email, subject, email_body)
            if success: return True, {"method": "Resend API", "to": target_email}

        # OPTION 2: Fallback to SMTP (Works locally)
        if self.sender_email and self.sender_password:
            try:
                msg = MIMEMultipart()
                msg['From'], msg['To'], msg['Subject'] = self.sender_email, target_email, subject
                msg.attach(MIMEText(email_body, 'plain'))
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
                return True, {"method": "Gmail SMTP", "to": target_email}
            except Exception as e:
                return False, f"SMTP Error: {str(e)}"

        return False, "No mailing method configured (Need Resend API Key or Gmail Credentials)"
