# Generated by Django 3.1.3 on 2021-01-21 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('databaseconnection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pipeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('pipeline_sql', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ViratualColumn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VirtualDatabase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('integration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='databaseconnection.integration')),
            ],
        ),
        migrations.CreateModel(
            name='VirtualSchema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('virtual_database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.virtualdatabase')),
            ],
        ),
        migrations.CreateModel(
            name='VirtualTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('virtual_schema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.virtualschema')),
            ],
        ),
        migrations.CreateModel(
            name='VirtualColumnAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('virtual_column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.viratualcolumn')),
            ],
        ),
        migrations.AddField(
            model_name='viratualcolumn',
            name='virtual_table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metadata.virtualtable'),
        ),
    ]
