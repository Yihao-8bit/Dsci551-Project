# Generated by Django 5.0.3 on 2025-04-11 05:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dsci551", "0004_alter_order_table"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="customer_id",
            field=models.ForeignKey(
                db_column="customer_id",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="dsci551.customer",
            ),
        ),
    ]
