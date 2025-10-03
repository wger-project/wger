from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('exercises', '0032_rename_exercise'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomExercise',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('is_public', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'category',
                    models.ForeignKey(
                        to='exercises.ExerciseCategory',
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                        related_name='custom_exercises',
                    ),
                ),
            ],
            options={
                'ordering': ['-created_at'],
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.AddField(
            model_name='customexercise',
            name='equipment',
            field=models.ManyToManyField(to='exercises.Equipment', blank=True),
        ),
        migrations.AddField(
            model_name='customexercise',
            name='primary_muscles',
            field=models.ManyToManyField(to='exercises.Muscle', blank=True),
        ),
    ]
