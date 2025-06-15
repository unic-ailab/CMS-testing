"""
accuracy_evaluation.py

This module evaluates the accuracy of a Count-Min Sketch (CMS) instance
by comparing its estimates to a ground truth dataset.

Usage:
    - Ensure that the CMS instance and ground truth are properly initialized.
    - If evaluating mid-stream, pass copies of both the CMS and ground truth
      to maintain consistency.
"""
import numpy as np
import heapq


def evaluate_accuracy(cms, ground_truth):
    """
    Evaluates the accuracy of a given Count-Min Sketch instance.

    If you use it mid-stream, be aware the CMS will keep evolving while the evaluation runs.
    Pass a copied CMS and ground_truth instances instead of the live ones.

    Args:
        cms: A CountMinSketch instance.
        ground_truth: A dictionary with ground truth counts.

    Returns:
        A dictionary containing the following:
            - 'avg_error': Average error
            - 'avg_error_percentage': Average error percentage
            - 'exact_match_percentage': Exact match percentage
            - 'overestimation_percentage': Overestimation percentage
            - 'percentiles': Dict with error percentiles (50th, 90th, 95th, 100th)
            - 'overestimated_items': List of (item, error), sorted by error desc
    """
    if not cms or not ground_truth:
        return "\nNo data to evaluate"

    test_items = list(ground_truth.keys())
    dataset_length = len(test_items)

    if not dataset_length:
        return "\nNo items processed"

    errors = []
    overestimations = []
    underestimations = []
    correct_count = 0

    for item in test_items:
        error = cms[item] - ground_truth[item]
        errors.append(error)

        if error == 0:
            correct_count += 1
        elif error > 0:
            overestimations.append((item, error))
        else:
            underestimations.append((item, error))

    avg_error = sum(abs(error) for error in errors) / dataset_length

    avg_error_percentage = sum(abs(err) / ground_truth[item] * 100 for item, err in zip(test_items, errors)) / dataset_length
    max_error_percentage = max(abs(err) / ground_truth[item] * 100 for item, err in zip(test_items, errors))

    exact_match_percentage = (correct_count / dataset_length) * 100
    overestimation_percentage = (len(overestimations) / dataset_length) * 100
    underestimation_percentage = (len(underestimations) / dataset_length) * 100

    top_20_overestimations = heapq.nlargest(20, overestimations, key=lambda x: x[1])
    top_20_underestimations = heapq.nsmallest(20, underestimations, key=lambda x: x[1])

    overestimation_percentiles = {}
    underestimation_percentiles = {}
    combined_percentiles = {}
    overestimation_errors = [error for _, error in overestimations]
    underestimation_errors = [abs(error) for _, error in underestimations]
    combined = overestimation_errors + underestimation_errors
    abs_combined = [abs(e) for e in combined]

    if overestimations:
        overestimation_percentiles = {
            "50th": np.percentile(overestimation_errors, 50),
            "90th": np.percentile(overestimation_errors, 90),
            "95th": np.percentile(overestimation_errors, 95),
            "100th": np.percentile(overestimation_errors, 100)
        }

    if underestimations:
        underestimation_percentiles = {
            "50th": np.percentile(underestimation_errors, 50),
            "90th": np.percentile(underestimation_errors, 90),
            "95th": np.percentile(underestimation_errors, 95),
            "100th": np.percentile(underestimation_errors, 100)
        }

    if underestimations or overestimations:
        combined_percentiles = {
            "50th": np.percentile(abs_combined, 50),
            "90th": np.percentile(abs_combined, 90),
            "95th": np.percentile(abs_combined, 95),
            "100th": np.percentile(abs_combined, 100)
        }

    return {
        'overestimation_percentage': overestimation_percentage,
        'underestimation_percentage': underestimation_percentage,
        'exact_match_percentage': exact_match_percentage,
        'avg_error': avg_error,
        'avg_error_percentage': avg_error_percentage,
        'max_error_percentage': max_error_percentage,
        'overestimation_percentiles': overestimation_percentiles,
        'underestimation_percentiles': underestimation_percentiles,
        'combined_percentiles': combined_percentiles,
        'top_20_overestimations': top_20_overestimations,
        'top_20_underestimations': top_20_underestimations
    }


def print_accuracy_evaluation(accuracy):
    overestimation_percentage = accuracy['overestimation_percentage']
    underestimation_percentage = accuracy['underestimation_percentage']
    exact_match_percentage = accuracy['exact_match_percentage']
    avg_error_percentage = accuracy['avg_error_percentage']
    avg_error = accuracy['avg_error']
    max_error_percentage = accuracy['max_error_percentage']

    over_percentiles = accuracy.get('overestimation_percentiles', {})
    under_percentiles = accuracy.get('underestimation_percentiles', {})
    combined_percentiles = accuracy.get('combined_percentiles', {})

    overestimations = accuracy['top_20_overestimations']
    underestimations = accuracy['top_20_underestimations']

    print(f"Exact Matches: {exact_match_percentage:.2f}%")
    print(f"Overestimations: {len(overestimations)} ({overestimation_percentage:.2f}%)")
    print(f"Underestimations: {len(underestimations)} ({underestimation_percentage:.2f}%)")
    print(f"Average Error: {avg_error:.3f}")
    print(f"Average Error Percentage: {avg_error_percentage:.2f}%")
    print(f"Max Error Percentage: {max_error_percentage:.2f}%")

    if over_percentiles:
        print("\nOverestimation Percentiles (error):")
        for percentile, value in over_percentiles.items():
            print(f"{percentile}: +{value:.2f}")

    if under_percentiles:
        print("\nUnderestimation Percentiles (absolute error):")
        for percentile, value in under_percentiles.items():
            print(f"{percentile}: -{value:.2f}")

    if combined_percentiles:
        print("\nCombined Percentiles (absolute error):")
        for percentile, value in combined_percentiles.items():
            print(f"{percentile}: {value:.2f}")

    print("\nTop Overestimations:")
    for item, error in overestimations[:10]:
        print(f"{item}: +{error}")

    print("\nTop Underestimations:")
    for item, error in underestimations[:10]:
        print(f"{item}: {error}")
