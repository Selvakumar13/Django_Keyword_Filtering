# Generated by Django 4.2.2 on 2023-07-06 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filter', '0004_urls_processed_urls'),
    ]

    operations = [
        migrations.AddField(
            model_name='urls',
            name='total_urls',
            field=models.IntegerField(default=0),
        ),
    ]