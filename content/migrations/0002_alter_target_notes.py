# Generated by Django 5.1.4 on 2024-12-13 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]