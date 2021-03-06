# Generated by Django 3.1.3 on 2021-01-21 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sqldialect', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseConnecion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('credential', models.TextField()),
                ('connection_type', models.CharField(choices=[('source', 'Source'), ('target', 'Target')], default='source', max_length=10)),
                ('sql_dialect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sqldialect.sqldialect')),
            ],
        ),
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('destination', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination', related_query_name='destination', to='databaseconnection.databaseconnecion')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source', related_query_name='source', to='databaseconnection.databaseconnecion')),
            ],
        ),
    ]
