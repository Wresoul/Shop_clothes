# Generated by Django 5.1.4 on 2024-12-23 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Название')),
                ('slug', models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='URL')),
            ],
            options={
                'verbose_name': 'Категорию',
                'verbose_name_plural': 'Категории',
                'db_table': 'category',
            },
        ),
        migrations.AlterModelOptions(
            name='goods',
            options={'verbose_name_plural': 'Товары'},
        ),
        migrations.AddField(
            model_name='goods',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=7, verbose_name='Скидка в %'),
        ),
        migrations.AddField(
            model_name='goods',
            name='slug',
            field=models.SlugField(blank=True, max_length=200, null=True, unique=True, verbose_name='URL'),
        ),
    ]
