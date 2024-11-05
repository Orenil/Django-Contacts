import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, app_password, recipient_email, subject, body):
    # Set up the server
    smtp_server = 'smtp.gmail.com'  # For Gmail; adjust if using another provider
    smtp_port = 587  # TLS port

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection with TLS

        # Login to your account
        server.login(sender_email, app_password)

        # Send the email
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        # Close the server connection
        server.quit()

# Usage example
send_email(
    sender_email="peteryuanlu1@gmail.com",
    app_password="havtczgjpfkopekk",
    recipient_email="thepeteryuanlu@gmail.com",
    subject="Test Email",
    body="This is a test email sent from Python."
)

