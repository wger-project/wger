# Generated by Django 4.2.6 on 2023-11-23 19:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('exercises', '0026_deletionlog_replaced_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deletionlog',
            name='replaced_by',
            field=models.UUIDField(
                default=None,
                editable=False,
                help_text='UUID of the object replaced by the deleted one. At the moment only available for exercise bases',
                null=True,
                verbose_name='Replaced by',
            ),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='exercisebase',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='exercisebase',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='exercisebase',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='exercisebase',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='exercisebase',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='exerciseimage',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='exerciseimage',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='exerciseimage',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='exerciseimage',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='exerciseimage',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='exercisevideo',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='exercisevideo',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='exercisevideo',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='exercisevideo',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='exercisevideo',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercise',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercise',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexercise',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercise',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexercise',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisebase',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisebase',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexercisebase',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisebase',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexercisebase',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexerciseimage',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexerciseimage',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexerciseimage',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexerciseimage',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexerciseimage',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisevideo',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=600,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisevideo',
            name='license_author_url',
            field=models.URLField(blank=True, verbose_name='Link to author profile, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexercisevideo',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a previous work, but which also contains sufficient new, creative content to entitle it to its own copyright.',
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisevideo',
            name='license_object_url',
            field=models.URLField(blank=True, verbose_name='Link to original object, if available'),
        ),
        migrations.AlterField(
            model_name='historicalexercisevideo',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=300,
                verbose_name='The original title of this object, if available',
            ),
        ),
    ]
