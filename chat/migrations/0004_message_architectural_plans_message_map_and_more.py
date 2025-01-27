# Generated by Django 5.0.6 on 2024-08-01 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('architectural_plans', '0005_alter_architecturalplan_units'),
        ('chat', '0003_message_sources'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='architectural_plans',
            field=models.ManyToManyField(help_text='Architectural plans recommended by bot', to='architectural_plans.architecturalplan'),
        ),
        migrations.AddField(
            model_name='message',
            name='map',
            field=models.JSONField(blank=True, help_text='Inner and outer polygons of parcel', null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='sent_by',
            field=models.CharField(choices=[('User', 'This message is sent from the user'), ('Bot', 'This message is generated from bot')], help_text='Message sent by Bot or User', max_length=20),
        ),
        migrations.AlterField(
            model_name='message',
            name='text',
            field=models.TextField(help_text='Text of the message', max_length=2000),
        ),
    ]
