# Generated by Django 5.1.4 on 2025-01-12 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_userbankaccount_account_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbankaccount',
            name='account_type',
            field=models.CharField(choices=[('Current', 'Current'), ('Savings', 'Savings')], max_length=10),
        ),
    ]
