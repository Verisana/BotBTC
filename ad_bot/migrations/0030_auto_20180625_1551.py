# Generated by Django 2.1b1 on 2018-06-25 10:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ad_bot', '0029_auto_20180625_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='adbottechnical',
            name='adbot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ad_bot.AdBot'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='adbottechnical',
            name='executed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adbottechnical',
            name='executing',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adbottechnical',
            name='message_executed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adbottechnical',
            name='message_executing',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adbottechnical',
            name='message_frequency',
            field=models.DurationField(blank=True, default='30', null=True),
        ),
    ]