# Generated by Django 4.2.6 on 2023-11-27 22:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_condutor_nota_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacao',
            name='para_condutor',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
