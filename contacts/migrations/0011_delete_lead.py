# Generated by Django 4.2.7 on 2023-12-08 17:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0010_lead_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Lead',
        ),
    ]
