# Generated by Django 4.2.7 on 2024-08-05 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0049_delete_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='email',
            name='subject',
            field=models.CharField(max_length=355),
        ),
    ]
