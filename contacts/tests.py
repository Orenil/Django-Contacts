from django.test import TestCase

{
    "smtpHost": "smtp.gmail.com",
    "smtpPort": 587,
    "mailUname": "followupreset1@gmail.com",
    "mailPwd": "anyosfcmarydmcns",
    "fromEmail": "oreoluwaadesina1999@gmail.com",
    "mailSubject": "test subject",
    "mailContentHtml": "Hi, Hope u are fine.",
    "recepientsMailList": ["oreoluwaadesina1999@gmail.com"]
}

{
    "host": "imap.gmail.com",
    "username": "followupreset1@gmail.com",
    "password": "anyosfcmarydmcns",
    "subject_keyword": "TEST"
}

Org_id = '174fc505-4a13-425c-9579-bf46339fbf98'

#Only One Step
{
    "email": "followupnowinfo@gmail.com",
    "password": "Beyourgreatestself123!",
    "campaign_name": "Test",
    "sequence_data": {
        "sequences": [
            {
                "steps": [
                    {
                        "type": "email",
                        "delay": 1,
                        "variants": [
                            {
                                "subject": "FollowUp test",
                                "body": "<div bis_skin_checked=\"1\">Save</div>"
                            }
                        ]
                    }
                ]
            }
        ],
        "campaignID": "0543c1fc-c1d9-42c4-afd1-7916c4ac17ac",
        "orgID": "174fc505-4a13-425c-9579-bf46339fbf98"
    }
}

#Multiple Steps
{
    "email": "followupnowinfo@gmail.com",
    "password": "Beyourgreatestself123!",
    "campaign_name": "Test",
    "sequence_data": {
        "sequences": [
            {
                "steps": [
                    {
                        "type": "email",
                        "delay": 1,
                        "variants": [
                            {
                                "subject": "FollowUp test",
                                "body": "<div bis_skin_checked=\"1\">I can do it</div>"
                            }
                        ]
                    },
                    {
                        "type": "email",
                        "delay": 2,
                        "variants": [
                            {
                                "subject": "FollowUp test",
                                "body": "<div bis_skin_checked=\"1\">Believe in yourself</div>"
                            }
                        ]
                    },
                    {
                        "type": "email",
                        "delay": 3,
                        "variants": [
                            {
                                "subject": "FollowUp test",
                                "body": "<div bis_skin_checked=\"1\">You can achieve things</div>"
                            }
                        ]
                    }
                ]
            }
        ],
        "campaignID": "0543c1fc-c1d9-42c4-afd1-7916c4ac17ac",
        "orgID": "174fc505-4a13-425c-9579-bf46339fbf98"
    }
}