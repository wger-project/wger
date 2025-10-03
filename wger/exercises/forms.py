# Django
from django import forms

# Local
from .models import CustomExercise


class CustomExerciseForm(forms.ModelForm):
    class Meta:
        model = CustomExercise
        fields = ['name', 'description', 'category', 'equipment', 'primary_muscles', 'is_public']
