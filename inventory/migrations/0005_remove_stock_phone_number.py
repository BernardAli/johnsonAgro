# Generated by Django 4.1.5 on 2023-01-20 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0004_alter_stock_returned_by_alter_stock_sale_to"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stock",
            name="phone_number",
        ),
    ]
