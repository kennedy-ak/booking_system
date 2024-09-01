# Generated by Django 5.1 on 2024-09-01 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0003_remove_transaction_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_type',
            field=models.CharField(choices=[('regular', 'single - 69 Cedis'), ('double', 'Double - 120 Cedis')], max_length=7),
        ),
    ]
