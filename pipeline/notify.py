import smtplib, ssl
from email.message import EmailMessage
from . import config

def send(subject, body):
    if not (config.GMAIL_ADDRESS and config.GMAIL_APP_PASSWORD and config.ALERT_EMAIL):
        print("[notify] email not configured; message was:\n", subject, "\n", body)
        return
    msg = EmailMessage()
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.ALERT_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
        s.send_message(msg)
