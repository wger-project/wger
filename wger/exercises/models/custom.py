# wger/exercises/models/custom.py
# Django
from django.conf import settings
from django.db import models


class CustomExercise(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='custom_exercises'
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        'exercises.ExerciseCategory', on_delete=models.SET_NULL, null=True, blank=True
    )

    equipment = models.ManyToManyField('exercises.Equipment', blank=True)
    primary_muscles = models.ManyToManyField('exercises.Muscle', blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = (('user', 'name'),)

    def __str__(self):
        return f'{self.name} ({self.user})'
