# Generated by Django 3.1.2 on 2020-11-03 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_deliveryorder_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryorder',
            name='delivery_items',
            field=models.ManyToManyField(blank=True, null=True, through='inventory.DeliveryItems', to='inventory.Item'),
        ),
    ]
