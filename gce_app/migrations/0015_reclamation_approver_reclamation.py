# Generated by Django 2.0 on 2018-05-11 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gce_app', '0014_auto_20180501_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='reclamation',
            name='approver_reclamation',
            field=models.BooleanField(db_column='approver_Reclamation', default=False),
        ),
    ]
