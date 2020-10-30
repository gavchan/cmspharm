# Generated by Django 3.1.2 on 2020-10-29 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drugdb', '0014_auto_20201029_1802'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='registereddrug',
            name='ingredients',
            field=models.ManyToManyField(related_name='registereddrugs', to='drugdb.Ingredient'),
        ),
    ]
