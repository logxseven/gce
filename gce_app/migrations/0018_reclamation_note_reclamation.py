# Generated by Django 2.0 on 2018-05-15 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gce_app', '0017_auto_20180515_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='reclamation',
            name='note_reclamation',
            field=models.FloatField(blank=True, db_column='note_Reclamation', null=True),
        ),
    ]
