# Generated by Django 5.1.5 on 2025-04-11 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QAEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lecture_id', models.IntegerField()),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('link', models.URLField(blank=True, null=True)),
            ],
        ),
    ]
