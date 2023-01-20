# Generated by Django 4.1.5 on 2023-01-20 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_stock"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="returned_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="inventory.customers",
            ),
        ),
        migrations.AlterField(
            model_name="stock",
            name="sale_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="sale_to",
                to="inventory.customers",
            ),
        ),
    ]
