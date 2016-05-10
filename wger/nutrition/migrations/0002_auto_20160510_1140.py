# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import wger.nutrition.models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField(verbose_name='Comment', blank=True)),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)])),
                ('ingredient', models.ForeignKey(verbose_name='Ingredient', to='nutrition.Ingredient')),
                ('plan', models.ForeignKey(editable=False, to='nutrition.NutritionPlan', verbose_name='Nutrition plan')),
                ('weight_unit', models.ForeignKey(verbose_name='Weight unit', blank=True, to='nutrition.IngredientWeightUnit', null=True)),
            ],
            bases=(wger.nutrition.models.BaseMealItem, models.Model),
        ),
        migrations.AlterField(
            model_name='meal',
            name='order',
            field=models.IntegerField(verbose_name='Order', editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='mealitem',
            name='order',
            field=models.IntegerField(verbose_name='Order', editable=False, blank=True),
        ),
    ]
