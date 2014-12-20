# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wger.utils.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('license_author', models.CharField(help_text='If you are not the author, enter the name or source here. This is needed for some licenses e.g. the CC-BY-SA.', max_length=50, null=True, verbose_name='Author', blank=True)),
                ('status', models.CharField(default=b'1', max_length=2, editable=False, choices=[(b'1', 'Pending'), (b'2', 'Accepted'), (b'3', 'Declined'), (b'4', 'Submitted by administrator'), (b'5', 'System ingredient')])),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Date')),
                ('update_date', models.DateField(auto_now=True, verbose_name='Date')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('energy', models.IntegerField(help_text='In kcal per 100g', verbose_name='Energy')),
                ('protein', models.DecimalField(help_text='In g per 100g of product', verbose_name='Protein', max_digits=6, decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('carbohydrates', models.DecimalField(help_text='In g per 100g of product', verbose_name='Carbohydrates', max_digits=6, decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('carbohydrates_sugar', models.DecimalField(decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], max_digits=6, blank=True, help_text='In g per 100g of product', null=True, verbose_name='Sugar content in carbohydrates')),
                ('fat', models.DecimalField(help_text='In g per 100g of product', verbose_name='Fat', max_digits=6, decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('fat_saturated', models.DecimalField(decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], max_digits=6, blank=True, help_text='In g per 100g of product', null=True, verbose_name='Saturated fat content in fats')),
                ('fibres', models.DecimalField(decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], max_digits=6, blank=True, help_text='In g per 100g of product', null=True, verbose_name='Fibres')),
                ('sodium', models.DecimalField(decimal_places=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], max_digits=6, blank=True, help_text='In g per 100g of product', null=True, verbose_name='Sodium')),
                ('language', models.ForeignKey(editable=False, to='core.Language', verbose_name='Language')),
                ('license', models.ForeignKey(default=2, verbose_name='License', to='core.License')),
                ('user', models.ForeignKey(blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='User')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IngredientWeightUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gram', models.IntegerField(verbose_name='Amount in grams')),
                ('amount', models.DecimalField(default=1, help_text='Unit amount, e.g. "1 Cup" or "1/2 spoon"', verbose_name='Amount', max_digits=5, decimal_places=2)),
                ('ingredient', models.ForeignKey(editable=False, to='nutrition.Ingredient', verbose_name='Ingredient')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(verbose_name='Order', max_length=1, editable=False, blank=True)),
                ('time', wger.utils.fields.Html5TimeField(null=True, verbose_name='Time (approx)', blank=True)),
            ],
            options={
                'ordering': ['time'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MealItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(verbose_name='Order', max_length=1, editable=False, blank=True)),
                ('amount', models.DecimalField(verbose_name='Amount', max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)])),
                ('ingredient', models.ForeignKey(verbose_name='Ingredient', to='nutrition.Ingredient')),
                ('meal', models.ForeignKey(editable=False, to='nutrition.Meal', verbose_name='Nutrition plan')),
                ('weight_unit', models.ForeignKey(verbose_name='Weight unit', blank=True, to='nutrition.IngredientWeightUnit', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NutritionPlan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Creation date')),
                ('description', models.TextField(help_text='A description of the goal of the plan, e.g. "Gain mass" or "Prepare for summer"', max_length=2000, verbose_name='Description', blank=True)),
                ('has_goal_calories', models.BooleanField(default=False, help_text='Tick the box if you want to mark this plan as having a goal amount of calories. You can use the calculator or enter the value yourself.', verbose_name='Use daily calories')),
                ('language', models.ForeignKey(editable=False, to='core.Language', verbose_name='Language')),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'ordering': ['-creation_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WeightUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('language', models.ForeignKey(editable=False, to='core.Language', verbose_name='Language')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='meal',
            name='plan',
            field=models.ForeignKey(editable=False, to='nutrition.NutritionPlan', verbose_name='Nutrition plan'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredientweightunit',
            name='unit',
            field=models.ForeignKey(verbose_name='Weight unit', to='nutrition.WeightUnit'),
            preserve_default=True,
        ),
    ]
