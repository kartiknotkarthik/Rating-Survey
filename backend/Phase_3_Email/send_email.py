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
            prompt = f"Analyze this report and provide: 1. A punchy professional subject line. 2. A warm 2-sentence intro. Respond in JSON: {{\"subject\": \"...\", \"intro\": \"...\"}}\n\nREPORT:\n{report_content[:3000]}"
            response = model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            return data.get("subject", "GROWW Weekly Pulse"), data.get("intro", "")
        except Exception:
            return "GROWW Weekly Pulse Report", ""

    def get_html_template(self, recipient_name, intro, report_md):
        # Clean formatting and prepare sections
        sections = report_md.split('---')
        content_html = ""
        
        for section in sections:
            # Remove MD artifacts and handle bolding/paragraphs
            lines = section.strip().split('\n')
            formatted_lines = []
            for line in lines:
                clean_line = line.strip().replace('*', '').replace('#', '')
                if not clean_line: continue
                
                # Check if it looks like a heading (short line or start of section)
                if len(clean_line) < 60 or ':' in clean_line:
                    formatted_lines.append(f"<p style='margin-bottom: 12px;'><strong>{clean_line}</strong></p>")
                else:
                    formatted_lines.append(f"<p style='margin-bottom: 18px;'>{clean_line}</p>")
            
            if formatted_lines:
                content_html += f"""
                <div style='margin-bottom: 25px; padding: 25px; background: #f9fbf9; border: 1px solid #e5e1da; border-left: 5px solid #00d09c;'>
                    {''.join(formatted_lines)}
                </div>
                """

        return f"""
        <html>
            <body style="font-family: 'Helvetica', 'Arial', sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 950px; margin: 0 auto; background-color: #fdfaf6; padding: 20px;">
                <div style="background-color: #ffffff; padding: 50px; border: 1px solid #e5e1da; border-top: 8px solid #00d09c;">
                    <div style="text-align: center; margin-bottom: 50px; border-bottom: 2px solid #1a1a1a; pb: 20px;">
                        <h1 style="font-style: italic; font-size: 48px; margin-bottom: 10px; color: #1a1a1a; font-family: 'Georgia', serif;">Groww <span style="color: #00d09c;">Pulse.</span></h1>
                        <p style="text-transform: uppercase; letter-spacing: 3px; font-size: 12px; color: #64748b; font-weight: bold;">Weekly Intelligence Editorial • Landscape Briefing</p>
                    </div>
                    
                    <div style="margin-bottom: 40px;">
                        <p style="font-size: 18px; margin-bottom: 10px;">Hi <strong>{recipient_name}</strong>,</p>
                        <p style="font-size: 18px; color: #475569; font-style: italic;">{intro}</p>
                    </div>
                    
                    <div style="display: grid; gap: 20px;">
                        {content_html}
                    </div>
                    
                    <footer style="margin-top: 60px; border-top: 1px solid #eee; padding-top: 30px; text-align: center; font-size: 11px; color: #94a3b8; text-transform: uppercase;">
                        © 2026 Groww Intelligence Bureau • Confidential Weekly Report
                    </footer>
                </div>
            </body>
        </html>
        """

    def send_via_resend(self, to_email, subject, html_content):
        url = "https://api.resend.com/emails"
        headers = {"Authorization": f"Bearer {self.resend_api_key}", "Content-Type": "application/json"}
        data = {
            "from": "Groww Pulse <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200, response.text

    def send_pulse_email(self, report_md, receiver_email=None, recipient_name="Team"):
        target_email = receiver_email if receiver_email else self.receiver_email
        if not target_email: return False, "No recipient email provided."

        subject, intro = self.generate_email_context(report_md)
        html_body = self.get_html_template(recipient_name, intro, report_md)

        if self.resend_api_key:
            success, msg = self.send_via_resend(target_email, subject, html_body)
            if success: return True, {"method": "Resend API", "to": target_email}

        if self.sender_email and self.sender_password:
            try:
                msg = MIMEMultipart()
                msg['From'], msg['To'], msg['Subject'] = self.sender_email, target_email, subject
                msg.attach(MIMEText(html_body, 'html'))
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(self.sender_email, self.sender_password)
                    server.send_message(msg)
                return True, {"method": "Gmail SMTP", "to": target_email}
            except Exception as e: return False, str(e)

        return False, "Configuration error."
