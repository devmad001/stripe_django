# Generated by Django 5.0.6 on 2024-07-01 06:58

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_report_architectural_plans_report_comparable_sales_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='report',
            unique_together={('user', 'address')},
        ),
    ]
