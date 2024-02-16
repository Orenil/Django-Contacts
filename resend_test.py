import resend

resend.api_key = "re_jSAHxBWL_7ZukqSxKcxeTbidSmgMdeuUq"

params = {
    "from": "hello@followup-networking.com",
    "to": "oreoluwaadesina1999@gmail.com",
    "subject": "hello world",
    "html": "<strong>it works!</strong>",
}

email = resend.Emails.send(params)
print(email)