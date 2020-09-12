# Generated by Django 3.1 on 2020-08-28 17:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('budget', '0004_auto_20200820_0318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expenses',
            name='eUser',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='expense_owner', to=settings.AUTH_USER_MODEL),
        ),
    ]
