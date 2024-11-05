import imaplib
import email
from email.header import decode_header

def check_email_response(imap_server, email_account, app_password, subject, recipient_email):
    # Connect to the IMAP server
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_account, app_password)
        
        # Select the mailbox you want to check (in this case, the inbox)
        mail.select("inbox")

        # Search for emails with the specified subject and recipient email
        status, response = mail.search(None, f'(SUBJECT "{subject}" FROM "{recipient_email}")')
        email_ids = response[0].split()

        if not email_ids:
            print("No responses found matching the subject and recipient email.")
            return

        # Fetch each email by ID and check if it’s a response
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    msg_subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(msg_subject, bytes):
                        msg_subject = msg_subject.decode()
                    msg_from = msg["From"]

                    print(f"Email from: {msg_from}, Subject: {msg_subject}")
                    
                    # Check if the email is a response (e.g., has 'Re:' or similar in the subject)
                    if msg_subject.startswith("Re:") or "Re:" in msg_subject:
                        print("Response detected!")
                        print(f"From: {msg_from}")
                        print(f"Subject: {msg_subject}")
                        print("=" * 50)
        
        # Close the connection
        mail.logout()
    
    except Exception as e:
        print(f"Error: {e}")

# Example usage
check_email_response(
    imap_server="imap.gmail.com",
    email_account="peteryuanlu1@gmail.com",
    app_password="havtczgjpfkopekk",
    subject="Test Email",
    recipient_email="thepeteryuanlu@gmail.com"
)
