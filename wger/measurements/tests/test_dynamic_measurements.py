# Standard Library
import unittest
from unittest.mock import (
    MagicMock,
    patch,
)

# wger
from wger.measurements.utils.bmi import calculate_bmi


class BMILogicTest(unittest.TestCase):
    """
    Pure unit test for BMI math logic.
    Bypasses Django database and wger signals.
    """

    @patch('wger.weight.models.WeightEntry.objects.filter')
    def test_calculate_bmi_math(self, mock_filter):
        user = MagicMock()
        user.userprofile.height = 180  # 1.8m

        weight_entry = MagicMock()
        weight_entry.weight = 80.0
        weight_entry.date = '2026-05-12'

        mock_filter.return_value.order_by.return_value = [weight_entry]

        results = calculate_bmi(user, category_id=99)

        # 80 / (1.8 * 1.8) = 24.69
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['value'], 24.69)
        self.assertEqual(results[0]['category'], 99)

    def test_calculate_bmi_missing_height(self):
        user = MagicMock()
        user.userprofile.height = None

        results = calculate_bmi(user, category_id=99)
        self.assertEqual(results, [])

    @patch('wger.weight.models.WeightEntry.objects.filter')
    def test_calculate_bmi_multiple_entries(self, mock_filter):
        user = MagicMock()
        user.userprofile.height = 175  # 1.75m

        w1 = MagicMock(weight=70.0, date='2026-05-01')
        w2 = MagicMock(weight=75.0, date='2026-05-10')

        mock_filter.return_value.order_by.return_value = [w1, w2]

        results = calculate_bmi(user, category_id=99)

        # 70 / 1.75^2 = 22.86
        self.assertEqual(results[0]['value'], 22.86)
        # 75 / 1.75^2 = 24.49
        self.assertEqual(results[1]['value'], 24.49)


if __name__ == '__main__':
    unittest.main()
