# Generated by Django 4.1.13 on 2024-05-14 19:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_application', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Chat',
        ),
        migrations.DeleteModel(
            name='Chat_Group',
        ),
        migrations.DeleteModel(
            name='Client_Commercial',
        ),
        migrations.DeleteModel(
            name='Client_Municipality',
        ),
        migrations.RemoveField(
            model_name='municipalitydata',
            name='permit',
        ),
        migrations.DeleteModel(
            name='Routes',
        ),
        migrations.DeleteModel(
            name='VerifyEmail',
        ),
        migrations.DeleteModel(
            name='VerifyForgetEmail',
        ),
        migrations.DeleteModel(
            name='Waitlist',
        ),
        migrations.DeleteModel(
            name='MunicipalityData',
        ),
        migrations.DeleteModel(
            name='MunicipalityPermit',
        ),
    ]
