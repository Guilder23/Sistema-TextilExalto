from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('materiales', '0002_costo_compra_precio_venta')]

    operations = [
        migrations.AddField('material', 'stock_critico', models.DecimalField(max_digits=12, decimal_places=2, default=0)),
    ]
