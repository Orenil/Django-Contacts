from django.test import TestCase
#for logging in
{
    "username": "Oreoluwa",
    "password": "Riverdale17@"
}

#for testing the send email
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

#for testing the read email
{
    "host": "imap.gmail.com",
    "username": "followupreset1@gmail.com",
    "password": "anyosfcmarydmcns",
    "subject_keyword": "TEST"
}

Org_id = '174fc505-4a13-425c-9579-bf46339fbf98'

#Only One Step for update sequence
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

#Multiple Steps for update sequence
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

#Upload to Campaign Emails Table database
{
    "selected_leads": [
        {
            "email": "example@email.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "ABC Inc.",
            "type": "Lead",
            "location": "City",
            "title": "Manager",
            "university": "XYZ University"
        },
        {
            "email": "another@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "DEF Corp.",
            "type": "Lead",
            "location": "Town",
            "title": "Director",
            "university": "PQR College"
        }
    ],
    "user_id": 1,
    "campaign_name": "Test"
}

#For upload to instantly campaign
{
    "selected_leads": [
        {
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "ABC Inc.",
            "type": "Lead",
            "title": "Manager",
            "university": "XYZ University"
        },
        {
            "email": "jane.smith@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "XYZ Corp.",
            "type": "Lead",
            "title": "Director",
            "university": "PQR College"
        }
    ],
    "campaign_name": "Test",
    "user_id": 24  
}

#for deleting leads from campaign on instantly
{
  "delete_list": [
    "daren@email.com"
  ],
  "campaign_name": "Test"
}

#for deleting leads from database
{
    "delete_list": [
        "john.doe@example.com"
    ],
    "campaign_name": "Test",
    "user_id": 24
}

#launch and pause campaign, campaign summary and campaign status
{
    "campaign_name": "Test"
}

#Save instructions model
{
    "user_id": 24,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "app_password": "secret443",
    "second_email": "johndoe2@example.com",
    "second_app_password": "secret456",
    "third_email": "johndoe3@example.com",
    "third_app_password": "secret789"
}
