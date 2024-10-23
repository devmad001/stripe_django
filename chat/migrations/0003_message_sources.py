# Generated by Django 5.0.6 on 2024-07-02 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chat_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='sources',
            field=models.JSONField(blank=True, help_text='List of the sources link coming from llm response', null=True),
        ),
    ]