# Generated by Django 2.0 on 2018-04-27 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gce_app', '0010_anneescolaire_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anneescolaire',
            name='active',
            field=models.BooleanField(db_column='active_Scolaire', unique=True),
        ),
    ]
