# Generated by Django 4.1.1 on 2022-09-08 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('username', models.CharField(default='', max_length=50)),
                ('email', models.CharField(default='', max_length=20, primary_key=True, serialize=False)),
                ('contact', models.IntegerField(default='')),
                ('age', models.IntegerField(default='')),
            ],
        ),
    ]
