# Generated by Django 4.2.1 on 2023-06-12 04:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_bids_listingactive_bids_winner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bids',
            name='listingActive',
        ),
        migrations.RemoveField(
            model_name='bids',
            name='winner',
        ),
        migrations.AddField(
            model_name='bids',
            name='isWinningBid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='listings',
            name='listingActive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='listings',
            name='listedBy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listedBy', to=settings.AUTH_USER_MODEL),
        ),
    ]
