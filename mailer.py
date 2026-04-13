import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_pulse_email(report_content):
    """
    Sends the weekly pulse report as an email.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    
    if not all([sender_email, sender_password, receiver_email]):
        print("Email credentials not fully configured in .env. Skipping email.")
        return False

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"GROWW Weekly Pulse - {os.getlogin()}'s Draft"

    # Attach the report as HTML/Markdown
    # For simplicity in many email clients, we send it as plain text or simple markdown
    body = f"""
    Hello Team,
    
    Here is the Weekly Pulse for GROWW based on recent Play Store reviews.
    
    ---
    {report_content}
    ---
    
    Regards,
    Pulse Automator
    """
    
    message.attach(MIMEText(body, "plain"))

    try:
        # Assuming Gmail SMTP for common use case, adjust if needed
        # smtp_server = "smtp.gmail.com"
        # smtp_port = 587
        
        # User might need to provide their own SMTP server config
        # We'll use a generic approach
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # Test
    test_report = "# Weekly Pulse\nTest content."
    send_pulse_email(test_report)
