import random
import time


def evaluate_avg_query_time(cms, ground_truth, threshold=100000):
    """
    Evaluates the average time of the query method of Sketch variation.

    Args:
        cms: The CountMinSketch instance to test.
        ground_truth: A dictionary containing the actual counts of items.
        threshold: The size above which sampling is used.

    Returns:
        Average query time per item.
    """
    total_items = len(ground_truth)
    if not total_items:  # nothing to evaluate
        return 0

    if total_items > threshold:
        test_items = random.sample(list(ground_truth.keys()), threshold)  # randomly sample 'threshold' items
    else:
        test_items = list(ground_truth.keys())

    start_time = time.time()
    for item in test_items:
        cms.query(item)
    end_time = time.time()

    avg_query_time = (end_time - start_time) / len(test_items)

    return avg_query_time


def print_avg_query_time(avg_query_time):
    print(f"Average query time per item: {avg_query_time:.12f} seconds")
