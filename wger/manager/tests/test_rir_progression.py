# This file is part of wger Workout Manager.
# ... (standard wger license header) ...

# Standard Library
from decimal import Decimal

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.manager.models import (
    SlotEntry,
    WeightConfig,
    WorkoutLog,
)
from wger.manager.models.abstract_config import (
    OperationChoices,
    StepChoices,
)


class RiRProgressionTestCase(WgerTestCase):
    """
    Test the RiR=0 percentage-based progression calculation logic
    """

    slot_entry: SlotEntry

    def setUp(self):
        super().setUp()

        self.slot_entry = SlotEntry(
            slot_id=1,
            exercise_id=1,
            order=1,
        )
        self.slot_entry.save()

    def test_rir_percent_calculation_explicit_baseline(self):
        """
        Test that WeightConfig correctly calculates the weight when rir_baseline is explicitly set.
        """
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=75,  # 75%
            operation=OperationChoices.REPLACE,
            step=StepChoices.RIR_PERCENT,
            rir_baseline=100.00,  # Explicit 1RM of 100
        ).save()

        # 100.00 * (75 / 100) = 75.00
        calculated_weight = self.slot_entry.calculate_weight(1)
        self.assertEqual(calculated_weight, Decimal('75.00'))

    def test_rir_percent_calculation_auto_detect_baseline(self):
        """
        Test that WeightConfig auto-detects the baseline from previous WorkoutLogs
        when rir_baseline is left blank (None).
        """
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=80,  # 80%
            operation=OperationChoices.REPLACE,
            step=StepChoices.RIR_PERCENT,
            rir_baseline=None,  # Rely on auto-detection
        ).save()

        # Create a log where the user lifted 120kg at RiR = 0 (100% effort)
        WorkoutLog.objects.create(
            user_id=1,
            routine_id=1,
            exercise_id=1,
            slot_entry=self.slot_entry,
            iteration=1,
            weight=120.00,
            repetitions=5,
            rir=Decimal('0.0'),  # Triggers auto-detect matching
        )

        # Create a distraction log with RiR = 2 (Should be ignored by auto-detect)
        WorkoutLog.objects.create(
            user_id=1,
            routine_id=1,
            exercise_id=1,
            slot_entry=self.slot_entry,
            iteration=1,
            weight=150.00,
            repetitions=5,
            rir=Decimal('2.0'),
        )

        # Should use 120.00 as baseline: 120.00 * (80 / 100) = 96.00
        calculated_weight = self.slot_entry.calculate_weight(1)
        self.assertEqual(calculated_weight, Decimal('96.00'))

    def test_rir_percent_missing_baseline_fallback(self):
        """
        Test that the calculation handles the absence of both an explicit
        baseline and valid logs gracefully.
        """
        WeightConfig(
            slot_entry=self.slot_entry,
            iteration=1,
            value=80,
            operation=OperationChoices.REPLACE,
            step=StepChoices.RIR_PERCENT,
            rir_baseline=None,
        ).save()

        # No RiR=0 logs exist. calculate_config_value should `continue` and leave `out` as 0.
        calculated_weight = self.slot_entry.calculate_weight(1)
        self.assertEqual(calculated_weight, Decimal('0'))

    def test_get_rir_baseline_prefers_explicit_over_logs(self):
        """
        Test that `get_rir_baseline` uses the explicit value even if logs exist.
        """
        config = WeightConfig.objects.create(
            slot_entry=self.slot_entry,
            iteration=1,
            value=80,
            step=StepChoices.RIR_PERCENT,
            rir_baseline=105.00,
        )

        # Log with RiR=0 exists, but should be ignored because explicit baseline is set
        WorkoutLog.objects.create(
            user_id=1,
            routine_id=1,
            exercise_id=1,
            slot_entry=self.slot_entry,
            iteration=1,
            weight=200.00,
            repetitions=1,
            rir=Decimal('0.0'),
        )

        baseline = self.slot_entry.get_rir_baseline(config)
        self.assertEqual(baseline, Decimal('105.00'))
