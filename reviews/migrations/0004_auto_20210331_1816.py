# Generated by Django 3.1.7 on 2021-03-31 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20210330_2009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreview',
            name='review',
            field=models.IntegerField(choices=[(1, 'Not relevant'), (2, 'Review'), (3, 'Maybe relevant'), (4, 'Relevant'), (5, 'Leading candidate')], default=3),
        ),
    ]