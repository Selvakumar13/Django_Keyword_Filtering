# Generated by Django 4.2.2 on 2023-07-17 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filter', '0007_urls_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='urls',
            name='status',
        ),
    ]
