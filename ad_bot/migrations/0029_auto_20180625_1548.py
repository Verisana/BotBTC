# Generated by Django 2.1b1 on 2018-06-25 10:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ad_bot', '0028_auto_20180624_1640'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adbottechnical',
            name='adbot',
        ),
        migrations.RemoveField(
            model_name='adbottechnical',
            name='executed_at',
        ),
        migrations.RemoveField(
            model_name='adbottechnical',
            name='executing',
        ),
        migrations.RemoveField(
            model_name='adbottechnical',
            name='message_executed_at',
        ),
        migrations.RemoveField(
            model_name='adbottechnical',
            name='message_executing',
        ),
        migrations.RemoveField(
            model_name='adbottechnical',
            name='message_frequency',
        ),
    ]
