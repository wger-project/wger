# wger/manager/tests/test_slotentry_custom_exercise.py
import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

# Adjust these imports to the actual names in your project if they differ
from wger.manager.models import Routine, Day, Slot, SlotEntry
from wger.exercises.models.custom import CustomExercise

@pytest.mark.django_db
def test_slotentry_clean_requires_one_choice():
    """Neither catalog nor custom selected should raise a validation error."""
    User = get_user_model()
    user = User.objects.create_user(username="tester", email="tester@example.com", password="pass123")
    routine = Routine.objects.create(user=user, name="Test Routine")   # adjust fields if needed
    day = Day.objects.create(routine=routine, day=1)                   # adjust fields if needed
    slot = Slot.objects.create(day=day, order=1)                       # adjust fields if needed

    entry = SlotEntry(slot=slot)  # no exercise, no custom_exercise
    with pytest.raises(ValidationError) as exc:
        entry.full_clean()  # calls SlotEntry.clean()
    assert "Select a catalog exercise or a custom one" in str(exc.value)

@pytest.mark.django_db
def test_slotentry_clean_rejects_both_selected():
    """Having both a catalog exercise and a custom one should raise a validation error."""
    User = get_user_model()
    user = User.objects.create_user(username="tester", email="tester@example.com", password="pass123")
    routine = Routine.objects.create(user=user, name="Test Routine")
    day = Day.objects.create(routine=routine, day=1)
    slot = Slot.objects.create(day=day, order=1)

    custom = CustomExercise.objects.create(user=user, name="Tempo Squat")
    entry = SlotEntry(slot=slot, custom_exercise=custom)
    entry.exercise_id = 999  # simulate a catalog exercise selected; full_clean doesn't verify FK existence

    with pytest.raises(ValidationError) as exc:
        entry.full_clean()
    assert "Pick either a catalog exercise or a custom one" in str(exc.value)

@pytest.mark.django_db
def test_slotentry_exercise_display_prefers_custom():
    """exercise_display returns the custom exercise when set."""
    User = get_user_model()
    user = User.objects.create_user(username="tester", email="tester@example.com", password="pass123")
    routine = Routine.objects.create(user=user, name="Test Routine")
    day = Day.objects.create(routine=routine, day=1)
    slot = Slot.objects.create(day=day, order=1)

    custom = CustomExercise.objects.create(user=user, name="Tempo Squat")
    entry = SlotEntry(slot=slot, custom_exercise=custom)

    assert entry.exercise_display == custom
