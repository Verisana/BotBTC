# Generated by Django 2.0.3 on 2018-06-11 15:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ad_bot', '0013_auto_20180611_1929'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenTrades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_id', models.IntegerField(null=True)),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='adbot',
            name='enable_autoposting',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adbot',
            name='farewell_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adbot',
            name='greetings_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='adbot',
            name='open_trades',
            field=models.ManyToManyField(to='ad_bot.OpenTrades'),
        ),
    ]
