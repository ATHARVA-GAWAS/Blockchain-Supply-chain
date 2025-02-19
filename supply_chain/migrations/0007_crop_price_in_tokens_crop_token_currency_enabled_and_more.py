# Generated by Django 5.1.2 on 2024-10-24 09:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supply_chain', '0006_crop_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='crop',
            name='price_in_tokens',
            field=models.FloatField(blank=True, help_text='Optional: Price in tokens for the crop.', null=True),
        ),
        migrations.AddField(
            model_name='crop',
            name='token_currency_enabled',
            field=models.BooleanField(default=False, help_text='Is token currency enabled for this crop?'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, default='default_profile.png', upload_to='profile_pictures/'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='token_balance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField(default=0.0, help_text='The number of tokens the user owns.')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
