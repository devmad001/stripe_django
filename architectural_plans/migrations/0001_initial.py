# Generated by Django 5.0.6 on 2024-06-15 18:02

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchitecturalPlan',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('plan_number', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=255)),
                ('image_link', models.URLField(default=False)),
                ('architectural_style', models.CharField(max_length=100)),
                ('area_total', models.FloatField()),
                ('bedrooms_count', models.FloatField()),
                ('bathrooms_count', models.FloatField()),
                ('bathrooms_full_count', models.FloatField()),
                ('bathrooms_half_count', models.FloatField()),
                ('stories', models.FloatField()),
                ('area_first_floor', models.FloatField()),
                ('area_second_floor', models.FloatField()),
                ('area_third_floor', models.FloatField()),
                ('area_basement', models.FloatField()),
                ('area_garage', models.FloatField()),
                ('cars_capacity', models.FloatField()),
                ('width', models.FloatField()),
                ('depth', models.FloatField()),
                ('buy_url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FavoritePlan',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('architectural_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='architectural_plans.architecturalplan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_plans', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
