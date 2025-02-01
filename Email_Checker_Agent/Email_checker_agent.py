import imaplib
import email
from email.header import decode_header

# Connect to the email server (example for Gmail)
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

# Process email content to check for certain keywords
def check_message_content(raw_email, keywords):
    msg = email.message_from_bytes(raw_email)
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()
    print(f"Checking email with subject: {subject}")
    
    keyword_found = False

    # Simple keyword checking in body
    body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    if body:
        for keyword in keywords:
            if keyword.lower() in body.lower():
                print(f"Keyword '{keyword}' found in message with subject: {subject}")
                keyword_found = True
                break
    return keyword_found

# Main agent loop
def message_checker_agent(email_username, email_password, keywords):
    mail = connect_to_email(email_username, email_password)
    
    while True:
        email_ids = fetch_unseen_emails(mail)
        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            raw_email = msg_data[0][1]
            if check_message_content(raw_email, keywords):
                # Placeholder: perform an action if keyword is found
                print("Taking action based on keyword detection")
        
        # Sleep or wait for some time before checking again
        time.sleep(60)  # Check emails every minute

if __name__ == "__main__":
    # Replace with real credentials
    email_username = "your_email@gmail.com"
    email_password = "your_password"
    
    # Keywords to check in incoming messages
    keywords = ["urgent", "meeting", "important"]

    message_checker_agent(email_username, email_password, keywords)