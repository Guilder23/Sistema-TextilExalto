from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('materiales', '0003_stock_critico')]

    operations = [
        migrations.AddField(
            model_name='material',
            name='imagen',
            field=models.ImageField(blank=True, upload_to='materiales/'),
        ),
    ]
