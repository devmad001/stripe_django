# Generated by Django 5.0.6 on 2024-06-22 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilesettings',
            name='facebook_page',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='instagram_profile',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='linkedin_profile',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='twitter_profile',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profilesettings',
            name='website_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
