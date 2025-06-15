import unittest
from unittest.mock import MagicMock
from evaluation.accuracy import evaluate_accuracy


class TestAccuracyEvaluation(unittest.TestCase):
    def setUp(self):
        """
        Setup mock ground truth for testing.
        """
        self.ground_truth = {
            'apple': 10,
            'banana': 20,
            'cherry': 30,
            'ginger': 40
        }

    def test_accuracy_perfect(self):
        """
        Test the accuracy evaluation when the CMS provides perfect matches.
        """
        mock_cms_perfect = MagicMock()

        def perfect_query_side_effect(item):
            return self.ground_truth.get(item, 0)

        mock_cms_perfect.query.side_effect = perfect_query_side_effect

        result = evaluate_accuracy(mock_cms_perfect, self.ground_truth)

        self.assertEqual(result['avg_error'], 0)  # No error
        self.assertEqual(result['avg_error_percentage'], 0)  # No error
        self.assertEqual(result['max_error_percentage'], 0)  # No error
        self.assertEqual(result['exact_match_percentage'], 100)  # All exact matches

    def test_accuracy_with_small_overestimation(self):
        """
        Test the accuracy evaluation with small overestimation.
        """
        mock_cms_small_overestimation = MagicMock()

        def small_overestimation_query_side_effect(item):
            cms_estimates = {
                'apple': 10,  # Exact match
                'banana': 22,  # Overestimated by 2
                'cherry': 30,  # Exact match
                'ginger': 41  # Overestimated by 1
            }
            return cms_estimates.get(item, 0)

        mock_cms_small_overestimation.query.side_effect = small_overestimation_query_side_effect

        result = evaluate_accuracy(mock_cms_small_overestimation, self.ground_truth)

        self.assertEqual(result['avg_error'], 0.75)  # Average error = (0+2+0+1)/4 = 0.75
        self.assertEqual(result['avg_error_percentage'], 3.125)  # (0 + 10 + 0 + 2.5) / 4
        # Max error is 2 (banana)
        self.assertEqual(result['max_error_percentage'], 10)  # (2 / 20) * 100 = 10 (banana)
        self.assertEqual(result['exact_match_percentage'], 50)  # There are 2 out of 4 exact matches

    def test_accuracy_with_large_overestimation(self):
        """
        Test the accuracy evaluation with large overestimation.
        """
        mock_cms_large_overestimation = MagicMock()

        def large_overestimation_query_side_effect(item):
            cms_estimates = {
                'apple': 15,  # Overestimated by 5
                'banana': 30,  # Overestimated by 10
                'cherry': 50,  # Overestimated by 20
                'ginger': 60  # Overestimated by 20
            }
            return cms_estimates.get(item, 0)

        mock_cms_large_overestimation.query.side_effect = large_overestimation_query_side_effect

        result = evaluate_accuracy(mock_cms_large_overestimation, self.ground_truth)

        self.assertEqual(result['avg_error'], 13.75)  # Average error = (5 + 10 + 20 + 20) / 4 = 13.75
        self.assertAlmostEqual(result['avg_error_percentage'], 54.16667, places=4)  # (50 + 50 + 66.6 + 50) / 4
        # Max error is 20 (cherry or ginger)
        self.assertAlmostEqual(result['max_error_percentage'], 2/3*100, places=4)  # (cherry 66.6% error)
        self.assertEqual(result['exact_match_percentage'], 0)  # No exact matches


if __name__ == '__main__':
    unittest.main()
