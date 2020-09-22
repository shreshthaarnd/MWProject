# Generated by Django 2.1.9 on 2020-09-21 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CSVData',
            fields=[
                ('File_ID', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('File_Name', models.CharField(max_length=15)),
                ('File_Src', models.ImageField(upload_to='csvfiles/')),
            ],
            options={
                'db_table': 'CSVData',
            },
        ),
    ]