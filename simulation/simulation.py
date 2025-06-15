import json
import os
import datetime
from evaluation.memory_usage import evaluate_memory_usage
from evaluation.avg_query_time import evaluate_avg_query_time
from evaluation.accuracy import evaluate_accuracy
from ground_truth.decaying_truth import DecayingTruth
from ground_truth.truth import Truth
from visualization.visualization import visualize
import copy
import argparse


def evaluate(cms, ground_truth):
    accuracy = evaluate_accuracy(cms, ground_truth)
    avg_query_time = evaluate_avg_query_time(cms, ground_truth)
    memory_usage = evaluate_memory_usage(cms)
    load_factor = cms.get_load_factor()

    return accuracy, avg_query_time, memory_usage, load_factor


def record_metrics(results_file, items_processed, accuracy, avg_query_time, memory_usage, load_factor):
    result = {
        "processed_items": int(items_processed),
        "avg_error": float(accuracy["avg_error"]),
        "avg_error_percentage": float(accuracy["avg_error_percentage"]),
        "overestimation_percentage": float(accuracy["overestimation_percentage"]),
        "underestimation_percentage": float(accuracy["underestimation_percentage"]),
        "exact_match_percentage": float(accuracy["exact_match_percentage"]),
        "avg_query_time": float(avg_query_time),
        "memory_usage": float(memory_usage),
        "load_factor": float(load_factor),
        "percentiles": {
            "overestimation": {
                "50th": float(accuracy.get("overestimation_percentiles", {}).get("50th", 0.0)),
                "90th": float(accuracy.get("overestimation_percentiles", {}).get("90th", 0.0)),
                "95th": float(accuracy.get("overestimation_percentiles", {}).get("95th", 0.0)),
                "100th": float(accuracy.get("overestimation_percentiles", {}).get("100th", 0.0)),
            },
            "underestimation": {
                "50th": float(accuracy.get("underestimation_percentiles", {}).get("50th", 0.0)),
                "90th": float(accuracy.get("underestimation_percentiles", {}).get("90th", 0.0)),
                "95th": float(accuracy.get("underestimation_percentiles", {}).get("95th", 0.0)),
                "100th": float(accuracy.get("underestimation_percentiles", {}).get("100th", 0.0)),
            },
            "combined": {
                "50th": float(accuracy.get("combined_percentiles", {}).get("50th", 0.0)),
                "90th": float(accuracy.get("combined_percentiles", {}).get("90th", 0.0)),
                "95th": float(accuracy.get("combined_percentiles", {}).get("95th", 0.0)),
                "100th": float(accuracy.get("combined_percentiles", {}).get("100th", 0.0)),
            }
        }
    }
    try:
        with open(results_file, "r") as f:
            existing_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_results = []
    existing_results.append(result)
    with open(results_file, "w") as f:
        json.dump(existing_results, f, indent=4)


def get_algorithm(algorithm, width, depth):
    if algorithm == "CountMinSketch":
        from summarization_algorithms.count_min_sketch import CountMinSketch
        cms = CountMinSketch(width=width, depth=depth)
    elif algorithm == "ConservativeCountMinSketch":
        from summarization_algorithms.conservative_count_min_sketch import ConservativeCountMinSketch
        cms = ConservativeCountMinSketch(width=width, depth=depth)
    elif algorithm == "CountMeanMinSketch":
        from summarization_algorithms.count_mean_min_sketch import CountMeanMinSketch
        cms = CountMeanMinSketch(width=width, depth=depth)
    elif algorithm == "CountSketch":
        from summarization_algorithms.count_sketch import CountSketch
        cms = CountSketch(width=width, depth=depth)
    elif algorithm == "SlidingCountMinSketch":
        from summarization_algorithms.sliding_count_min_sketch import SlidingCountMinSketch
        cms = SlidingCountMinSketch(width=width, depth=depth)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    return cms


def get_truth_class(config):
    if config["algorithm"] == "SlidingCountMinSketch":
        return DecayingTruth(window_size=config["width"]*config["depth"])
    return Truth()


def get_stream_simulator(config):

    if config["dataset_name"] == "synthetic":
        from input_stream.random_stream_simulator import RandomStreamSimulator
        return RandomStreamSimulator(sleep_time=config["sleep_time"])
    else:
        from input_stream.dataset_stream_simulator import DatasetStreamSimulator
        return DatasetStreamSimulator(
            dataset_path=f"../datasets/{config['dataset_name']}",
            field_name=config["field"],
            sleep_time=config["sleep_time"]
        )


def eval_and_record(cms, ground_truth, file_path):
    accuracy, query_speed, memory_usage, load_factor = evaluate(copy.deepcopy(cms), ground_truth.get_all())
    record_metrics(file_path, cms.totalCount, accuracy, query_speed, memory_usage, load_factor)


if __name__ == '__main__':
    with open("../config.json", "r") as f:
        CONFIG = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument('--algorithm', required=True, help='Algorithm to use')
    parser.add_argument('--dataset', required=True, help='Dataset to use')
    parser.add_argument('--width', type=int, help='Width parameter for CMS')
    parser.add_argument('--depth', type=int, help='Depth parameter for CMS')
    parser.add_argument('--timestamp', required=False)
    args = parser.parse_args()

    if args.width is not None:
        CONFIG['width'] = args.width
    if args.depth is not None:
        CONFIG['depth'] = args.depth

    WIDTH = CONFIG["width"]
    DEPTH = CONFIG["depth"]
    ALGORITHM = args.algorithm
    EVAL_INTERVAL = CONFIG["eval_interval"]
    VIS_INTERVAL = CONFIG["vis_interval"]
    if args.dataset:
        CONFIG['dataset_name'] = args.dataset
    DATASET_NAME = CONFIG["dataset_name"]

    stream_simulator = get_stream_simulator(CONFIG)
    cms = get_algorithm(ALGORITHM, WIDTH, DEPTH)
    ground_truth = get_truth_class(CONFIG)

    timestamp = args.timestamp or datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    RESULTS_DIR = f"../experiments/{DATASET_NAME}/{ALGORITHM}/w{cms.width}_d{cms.depth}/{timestamp}"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    RESULTS_FILE = os.path.join(RESULTS_DIR, "results.json")
    PLOTS_DIR = RESULTS_DIR

    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "w") as f:
            json.dump([], f)

    for item in stream_simulator.simulate_stream():
        cms.add(item)
        ground_truth.add(item)

        if cms.totalCount % EVAL_INTERVAL == 0:
            eval_and_record(cms, ground_truth, RESULTS_FILE)

        if cms.totalCount % VIS_INTERVAL == 0:
            visualize(RESULTS_FILE, PLOTS_DIR)

    eval_and_record(cms, ground_truth, RESULTS_FILE)
    visualize(RESULTS_FILE, PLOTS_DIR)
