import datetime

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from wger.nutrition.models.fasting import FastingWindow
from wger.core.models.language import Language  


User = get_user_model()


class FastingWindowTestCase(TestCase):
    def setUp(self) -> None:
        Language.objects.get_or_create(
            pk=2,
            defaults={
                "short_name": "en",
                "full_name": "English",
                "full_name_en": "English",
            },
        )

        self.user = User.objects.create_user(
            username="fasting_tester",
            email="tester@example.com",
            password="secure-password",
        )

    def test_create_minimal_fasting_window(self):
        window = FastingWindow.objects.create(user=self.user)

        self.assertEqual(window.user, self.user)
        self.assertIsNotNone(window.start)
        self.assertIsNone(window.end)
        self.assertIsNone(window.goal_duration_minutes)
        self.assertEqual(window.note, "")

    def test_is_active_true_when_end_is_none(self):
        window = FastingWindow.objects.create(
            user=self.user,
            end=None,
        )
        self.assertTrue(window.is_active)

    def test_is_active_false_when_end_is_set(self):
        now = timezone.now()
        later = now + datetime.timedelta(hours=1)

        window = FastingWindow.objects.create(
            user=self.user,
            start=now,
            end=later,
        )
        self.assertFalse(window.is_active)

    def test_duration_and_duration_seconds_for_finished_fast(self):
        start = timezone.now()
        end = start + datetime.timedelta(hours=1, minutes=30)  # 1.5 hours

        window = FastingWindow.objects.create(
            user=self.user,
            start=start,
            end=end,
        )

        expected_delta = end - start
        self.assertEqual(window.duration, expected_delta)
        self.assertEqual(window.duration_seconds, int(expected_delta.total_seconds()))
        self.assertEqual(window.duration_seconds, 90 * 60)

    def test_duration_for_active_fast_is_positive(self):
        window = FastingWindow.objects.create(user=self.user)
        self.assertTrue(window.is_active)

        duration = window.duration
        self.assertGreater(duration.total_seconds(), 0)

    def test_goal_duration_minutes_optional_and_stored(self):
        window_without_goal = FastingWindow.objects.create(user=self.user)
        self.assertIsNone(window_without_goal.goal_duration_minutes)

        goal_minutes = 16 * 60
        window_with_goal = FastingWindow.objects.create(
            user=self.user,
            goal_duration_minutes=goal_minutes,
        )
        self.assertEqual(window_with_goal.goal_duration_minutes, goal_minutes)

    def test_str_representation_contains_user_and_start(self):
        start = timezone.now()
        window = FastingWindow.objects.create(
            user=self.user,
            start=start,
        )

        text = str(window)
        self.assertIn(self.user.username, text)
        self.assertIn(str(start.date()), text)

    def test_get_owner_object_returns_self(self):
        window = FastingWindow.objects.create(user=self.user)
        self.assertIs(window.get_owner_object(), window)

    def test_ordering_by_start_descending(self):
        older_start = timezone.now() - datetime.timedelta(hours=5)
        newer_start = timezone.now()

        older = FastingWindow.objects.create(
            user=self.user,
            start=older_start,
        )
        newer = FastingWindow.objects.create(
            user=self.user,
            start=newer_start,
        )

        windows = list(FastingWindow.objects.all())
        self.assertEqual(windows[0], newer)
        self.assertEqual(windows[1], older)
