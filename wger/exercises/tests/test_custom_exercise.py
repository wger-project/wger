# wger/exercises/tests/test_custom_exercise.py
import pytest
from django.contrib.auth import get_user_model
from wger.exercises.models.custom import CustomExercise

@pytest.mark.django_db
def test_create_custom_exercise_for_user():
    User = get_user_model()
    user = User.objects.create_user(username="tester", email="tester@example.com", password="pass123")

    custom = CustomExercise.objects.create(
        user=user,
        name="Tempo Squat",
        description="User-defined tempo squat",
    )

    assert custom.pk is not None
    assert custom.user == user
    assert custom.name == "Tempo Squat"
