# Generated by Django 5.1.4 on 2024-12-21 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_alter_order_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='menu_items'),
        ),
    ]
