# Generated by Django 5.1.1 on 2025-04-04 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('rarity', models.CharField(default='Common', max_length=50)),
                ('quantity', models.IntegerField(default=1)),
            ],
        ),
    ]
