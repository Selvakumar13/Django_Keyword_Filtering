# Generated by Django 4.2.2 on 2023-07-17 05:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filter', '0005_urls_total_urls'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='urls',
            name='processed_urls',
        ),
        migrations.RemoveField(
            model_name='urls',
            name='total_urls',
        ),
    ]
