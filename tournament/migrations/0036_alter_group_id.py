# Generated by Django 4.2.4 on 2023-08-27 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0035_delete_clubhistory"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
