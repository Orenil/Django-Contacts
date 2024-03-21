import requests

url = "https://api.brevo.com/v3/smtp/email"

payload = {
    "sender": {
        "name": "Enoch_Test",
        "email": "oreoluwaadesina1999@gmail.com",
        "id": 2
    },
    "to": [
        {
            "email": "samueladesina538@gmail.com",
            "name": "Samuel"
        }
    ],
    "htmlContent": "<!DOCTYPE html> <html> <body> <h1>Confirm you email</h1> <p>Please confirm your email address by clicking on the link below</p> </body> </html>",
    "textContent": "Please confirm your email address by clicking on the link https://text.domain.com",
    "subject": "Login Email confirmation",
    "replyTo": {
        "email": "oreoluwaadesina1999@gmail.com",
        "name": "Enoch"
    },
    "attachment": [
        {
            "url": "https://attachment.domain.com/myAttachmentFromUrl.jpg",
            "content": "b3JkZXIucGRm",
            "name": "myAttachment.png"
        }
    ],
    "headers": {
        "sender.ip": "1.2.3.4",
        "X-Mailin-custom": "some_custom_header",
        "idempotencyKey": "abc-123"
    },
    "templateId": 2,
    "params": {
        "FNAME": "Joe",
        "LNAME": "Doe"
    },
    "messageVersions": [
        {
            "to": [
                {
                    "email": "jimmy98@example.com",
                    "name": "Jimmy"
                }
            ],
            "params": {
                "FNAME": "Joe",
                "LNAME": "Doe"
            },
            "subject": "Login Email confirmation"
        }
    ],
    "tags": ["tag1"],
    "scheduledAt": "2022-04-05T12:30:00+02:00",
    "batchId": "5c6cfa04-eed9-42c2-8b5c-6d470d978e9d"
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "api-key": "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"
}

response = requests.post(url, json=payload, headers=headers)

print(response.text)