# Generated by Django 5.0.6 on 2024-09-09 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_crm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='waitlistuser',
            name='comments',
            field=models.TextField(blank=True, help_text='Field to store user comments', max_length=2000, null=True),
        ),
    ]