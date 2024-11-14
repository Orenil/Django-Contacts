import imaplib
import email
from email.utils import parseaddr
from django.core.mail import send_mail
from django.conf import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

def check_for_reply_task(host, username, password, subject_keyword, recipient_email):
    logger.info("Starting check_for_reply_task...")

    try:
        # Connect to the email server
        mail = imaplib.IMAP4_SSL(host)
        mail.login(username, password)
        mail.select("inbox")

        # Search for emails with the specified subject
        status, search_data = mail.search(None, f'(SUBJECT "{subject_keyword}")')
        if status != 'OK':
            logger.error(f"Error searching emails: {search_data}")
            return False

        search_data = search_data[0].split()

        for num in search_data:
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                logger.error(f"Error fetching email: {data}")
                continue

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            from_email = parseaddr(msg['From'])[1]

            # Check if the reply is from the recipient email
            if from_email == recipient_email:
                logger.info(f"Found reply from {recipient_email}")
                mail.close()
                mail.logout()
                return True  # Found a reply

        mail.close()
        mail.logout()
        logger.info("No reply found.")
        return False  # No reply found
    except Exception as e:
        logger.error(f"Error in check_for_reply_task: {str(e)}")
        return False

def send_followup_email(subject, body, recipient_email):
    logger.info(f"Sending follow-up email to {recipient_email} with subject '{subject}'")

    try:
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )
        logger.info(f"Sent follow-up email to {recipient_email}")
    except Exception as e:
        logger.error(f"Error sending follow-up email: {str(e)}")

