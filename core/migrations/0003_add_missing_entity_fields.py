from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_entity_city_entity_phone2_entity_woreda_and_more'),  # replace with the actual latest migration file name
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='phone2',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='entity',
            name='woreda',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]