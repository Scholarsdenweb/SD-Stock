# Generated by Django 5.2 on 2025-05-16 03:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='enrollement',
            field=models.CharField(max_length=15, unique=True, validators=[django.core.validators.RegexValidator('^\\d+$')]),
        ),
    ]
