# Generated by Django 5.0.6 on 2024-06-22 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('architectural_plans', '0002_alter_architecturalplan_area_basement_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='architecturalplan',
            name='buy_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='image_link',
            field=models.URLField(),
        ),
    ]