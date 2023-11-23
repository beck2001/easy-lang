# Generated by Django 4.2.7 on 2023-11-18 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0007_alter_user_img_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approve',
            name='pages_per_day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.pages_per_day', unique=True),
        ),
        migrations.AlterField(
            model_name='disapprove',
            name='pages_per_day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.pages_per_day', unique=True),
        ),
    ]
