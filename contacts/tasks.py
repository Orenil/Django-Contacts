from celery import shared_task
from django.core.mail import send_mail
import time
from django.conf import settings
import imaplib
import email
from email.utils import parseaddr

@shared_task
def send_follow_up_email_task(subject, body, recipient_email):
    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [recipient_email],
        fail_silently=False,
    )

@shared_task
def check_for_replies_task(username, password, host, subject_keyword, recipient_email, followup_subject, followup_body,
                           wait_time, check_interval, second_followup_subject, second_followup_body, second_wait_time):

    def check_for_reply():
        """
        Checks the inbox for replies from the recipient with the matching subject keyword.
        """
        mail.select("inbox")  # Select the inbox folder
        status, search_data = mail.search(None, '(SUBJECT "{}")'.format(subject_keyword))
        search_data = search_data[0].split()

        # Check if any emails are replies from the recipient
        for num in search_data:
            status, data = mail.fetch(num, '(RFC822)')  # Fetch the entire email (headers and body)
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract the 'From' email address
            from_email = parseaddr(msg['From'])[1]

            # Check if the reply is from the recipient_email
            if from_email == recipient_email:
                return True
        return False

    # Connect to the email server using the sender's (username) credentials
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)

    # Check if a reply has already been received before sending the first follow-up
    if check_for_reply():
        mail.close()
        mail.logout()
        return "Recipient already replied. No follow-up email sent."

    # If no reply is found, wait for the specified time and send the first follow-up email
    time.sleep(wait_time * 60)  # Wait time in minutes
    send_follow_up_email_task(followup_subject, followup_body, recipient_email)

    # After sending the first follow-up, take a short pause and recheck for replies
    time.sleep(check_interval * 60)  # Pause before checking inbox again
    if check_for_reply():
        mail.close()
        mail.logout()
        return "Recipient replied after the first follow-up. No second follow-up email sent."

    # If no reply after checking again, wait for the second wait time and send the second follow-up
    time.sleep(second_wait_time * 60)  # Second wait time in minutes
    if not check_for_reply():  # Check one final time before sending the second follow-up
        send_follow_up_email_task(second_followup_subject, second_followup_body, recipient_email)
        mail.close()
        mail.logout()
        return "Second follow-up email sent."
    else:
        # If the recipient replied during the second wait time
        mail.close()
        mail.logout()
        return "Recipient replied before the second follow-up."
