# Generated by Django 5.1.5 on 2025-01-29 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='books',
            name='name',
            field=models.TextField(verbose_name='Books description'),
        ),
    ]
