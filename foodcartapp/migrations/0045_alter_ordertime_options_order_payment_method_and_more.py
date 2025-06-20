# Generated by Django 4.2.22 on 2025-06-14 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_alter_ordertime_options_remove_ordertime_creation_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ordertime',
            options={'verbose_name': 'Время заказа'},
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'наличные'), ('card', 'карта')], db_index=True, default=' ', max_length=10, verbose_name='Способ оплаты'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'новый'), ('work', 'в работе'), ('completed', 'завершён'), ('delivery', 'доставка'), ('accept', 'принят')], db_index=True, default='new', max_length=10, verbose_name='Статус'),
        ),
    ]
