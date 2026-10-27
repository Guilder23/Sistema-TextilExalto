from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('materiales', '0001_initial')]

    operations = [
        migrations.RenameField('material', 'costo_unitario', 'costo_compra'),
        migrations.AddField('material', 'precio_venta', models.DecimalField(max_digits=12, decimal_places=2, default=0)),
    ]
