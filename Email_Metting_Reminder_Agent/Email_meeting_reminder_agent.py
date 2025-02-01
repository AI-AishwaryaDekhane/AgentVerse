import imaplib
import email
from email.header import decode_header
import schedule
import time
from datetime import datetime, timedelta

# Connect to the email server
def connect_to_email(username, password, server='imap.gmail.com'):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(username, password)
    return mail

# Fetch unseen emails
def fetch_unseen_emails(mail):
    mail.select("inbox")
    result, data = mail.search(None, '(UNSEEN)')
    email_ids = data[0].split()
    return email_ids

# Process email content to extract reminder information
def process_email_content(raw_email):
    msg = email.message_from_bytes(raw_email)
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()

    # Simplified content extraction
    body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    return subject, body

# Set a reminder based on the email content
def set_reminder(subject, body, time_offset=5):
    # For demonstration purposes, we are setting a reminder 5 minutes after receiving the email.
    reminder_time = datetime.now() + timedelta(minutes=time_offset)
    print(f"Setting reminder for email: {subject} at {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")
    # Here you could use a more sophisticated system like integrating with a calendar API.
    schedule.every().day.at(reminder_time.strftime('%H:%M')).do(lambda: print(f"Reminder: {subject}"))

# Main agent loop
def email_agent(email_username, email_password):
    mail = connect_to_email(email_username, email_password)
    
    while True:
        email_ids = fetch_unseen_emails(mail)
        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            raw_email = msg_data[0][1]
            subject, body = process_email_content(raw_email)
            # In real application, further NLP would extract details like reminder date/time/keywords.
            set_reminder(subject, body)
        
        # Run scheduled reminders
        schedule.run_pending()
        time.sleep(60)  # Check emails every minute

if __name__ == "__main__":
    # Replace with real credentials
    email_username = "your_email@gmail.com"
    email_password = "your_password"
    email_agent(email_username, email_password)