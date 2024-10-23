# Generated by Django 5.0.6 on 2024-06-16 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('architectural_plans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_basement',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_first_floor',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_garage',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_second_floor',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_third_floor',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='area_total',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bathrooms_count',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bathrooms_full_count',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bathrooms_half_count',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='bedrooms_count',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='buy_url',
            field=models.URLField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='cars_capacity',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='depth',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='stories',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='architecturalplan',
            name='width',
            field=models.FloatField(default=0.0),
        ),
    ]
