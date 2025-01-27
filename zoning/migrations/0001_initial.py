# Generated by Django 5.0.6 on 2024-06-19 11:35

import django.contrib.gis.db.models.fields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GISZoning',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('object_id', models.FloatField(blank=True, help_text='Unique identifier for the zoning object, typically used for internal reference.', null=True)),
                ('zone_type', models.CharField(blank=True, help_text='Type of zoning (e.g., residential, commercial, industrial).', max_length=254, null=True)),
                ('zoning_desc', models.CharField(blank=True, help_text='Detailed description of the zoning designation.', max_length=254, null=True)),
                ('ordinance', models.CharField(blank=True, help_text='Reference to the ordinance or legal document defining the zoning regulations.', max_length=254, null=True)),
                ('city', models.CharField(blank=True, help_text='Name of the city where the zoning area is located.', max_length=50, null=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(blank=True, help_text='Geometric representation of the zoning area, typically stored as polygons or multipolygons.', null=True, srid=4326)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
