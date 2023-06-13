# Generated by Django 4.1.5 on 2023-01-26 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerDetails',
            fields=[
                ('customer_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=100)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('username', models.CharField(max_length=200)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
                ('mobile', models.CharField(blank=True, max_length=50, null=True)),
                ('addrLine1', models.CharField(blank=True, max_length=200, null=True)),
                ('addrLine2', models.CharField(blank=True, max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('pincode', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(default='India', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='AppUser',
        ),
    ]