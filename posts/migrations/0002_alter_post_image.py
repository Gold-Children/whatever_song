# Generated by Django 4.2 on 2024-06-09 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, default='posts/post_pic/main logo.png/', null=True, upload_to='posts/post_pic/%Y/%m/%d/'),
        ),
    ]
