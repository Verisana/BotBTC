# Generated by Django 2.1b1 on 2018-06-24 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad_bot', '0026_auto_20180624_1357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adbottechnical',
            name='message_frequency',
            field=models.DurationField(blank=True, default='30', null=True),
        ),
    ]
