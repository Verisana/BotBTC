# Generated by Django 2.0.3 on 2018-04-03 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad_bot', '0002_auto_20180404_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adbot',
            name='trade_direction',
            field=models.CharField(choices=[('buy-bitcoins-online', 'ONLINE_SELL'), ('sell-bitcoins-online', 'ONLINE_BUY')], max_length=64),
        ),
    ]