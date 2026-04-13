import os
import smtplib
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
        
        if not all([self.sender_email, self.sender_password, self.receiver_email]):
            raise ValueError("Email credentials missing in .env (SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL)")

    def generate_email_context(self, report_content):
        """
        Uses Gemini to generate a professional subject and executive summary.
        """
        if not google_api_key:
            return "GROWW Weekly Pulse Report", ""

        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            prompt = f"""
            Analyze this report and provide two things:
            1. A short, professional email subject line.
            2. A 2-sentence executive summary to be used as the intro of the email.
            
            REPORT:
            {report_content[:3000]}
            
            Respond ONLY in JSON format like: {{"subject": "...", "intro": "..."}}
            """
            
            response = model.generate_content(prompt)
            data = json.loads(response.text.replace('```json', '').replace('```', '').strip())
            return data.get("subject", "GROWW Weekly Pulse"), data.get("intro", "")
        except Exception as e:
            print(f"Gemini Refinement Error: {e}")
            return "GROWW Weekly Pulse Report", ""

    def send_pulse_email(self, report_md, receiver_email=None, recipient_name="Team"):
        """
        Sends the pulse report as an email with personalization.
        """
        target_email = receiver_email if receiver_email else self.receiver_email
        if not target_email:
            return False, "No recipient email provided."

        subject, intro = self.generate_email_context(report_md)
        
        # Build email body with personalization
        greeting = f"Hi {recipient_name}!\n\n"
        email_body = f"{greeting}{intro}\n\n---\n\n{report_md}"
        
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = target_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(email_body, 'plain'))
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            return True, {"subject": subject, "to": target_email, "name": recipient_name}
        except Exception as e:
            return False, str(e)

if __name__ == "__main__":
    import sys
    # Check for report from Phase 2
    report_file = os.path.join(base_dir, "reports", "weekly_pulse_note.md")
    
    if not os.path.exists(report_file):
        print(f"Report file not found at {report_file}. Please run Phase 2 first.")
    else:
        with open(report_file, 'r') as f:
            report_content = f.read()
            
        # Get recipient and name from CLI or fallback to .env/default
        cli_recipient = sys.argv[1] if len(sys.argv) > 1 else None
        cli_name = sys.argv[2] if len(sys.argv) > 2 else "Team"
        
        mailer = GrowwMailerPhase3()
        print(f"Crafting personalized email for {cli_name}...")
        success, info = mailer.send_pulse_email(report_content, receiver_email=cli_recipient, recipient_name=cli_name)
        
        if success:
            print(f"Successfully sent email to {info['name']} ('{info['to']}') with subject: '{info['subject']}'")
        else:
            print(f"Failed to send email: {info}")
