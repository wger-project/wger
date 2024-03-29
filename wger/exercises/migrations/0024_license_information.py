# Generated by Django 4.2 on 2023-04-07 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('exercises', '0023_make_uuid_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercise',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='exercise',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercise',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercisebase',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercisebase',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='exercisebase',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercisebase',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AddField(
            model_name='exerciseimage',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='exerciseimage',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='exerciseimage',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='exerciseimage',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercisevideo',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercisevideo',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='exercisevideo',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='exercisevideo',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercise',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercise',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercise',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercise',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisebase',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisebase',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisebase',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisebase',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexerciseimage',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexerciseimage',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='historicalexerciseimage',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexerciseimage',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisevideo',
            name='license_author_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to author profile, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisevideo',
            name='license_derivative_source_url',
            field=models.URLField(
                blank=True,
                help_text='Note that a derivative work is one which is not only based on a '
                'previous work, but which also contains sufficient new, creative '
                'content to entitle it to its own copyright.',
                max_length=100,
                verbose_name='Link to the original source, if this is a derivative work',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisevideo',
            name='license_object_url',
            field=models.URLField(
                blank=True,
                max_length=100,
                verbose_name='Link to original object, if available',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercisevideo',
            name='license_title',
            field=models.CharField(
                blank=True,
                max_length=200,
                verbose_name='The original title of this object, if available',
            ),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='exercisebase',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='exerciseimage',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='exercisevideo',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercise',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisebase',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexerciseimage',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
        migrations.AlterField(
            model_name='historicalexercisevideo',
            name='license_author',
            field=models.CharField(
                blank=True,
                help_text='If you are not the author, enter the name or source here.',
                max_length=200,
                null=True,
                verbose_name='Author(s)',
            ),
        ),
    ]
