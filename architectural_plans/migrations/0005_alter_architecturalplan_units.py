# Generated by Django 5.0.6 on 2024-06-27 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('architectural_plans', '0004_exteriorwalltype_foundation_garagelocation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='architecturalplan',
            name='units',
            field=models.FloatField(default=0.0, help_text='Units correspond to plan types like single family, stand alone etc'),
        ),
    ]