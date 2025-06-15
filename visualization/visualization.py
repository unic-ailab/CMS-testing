import json
import matplotlib.pyplot as plt
import os


def load_results(filepath):
    with open(filepath, "r") as file:
        return json.load(file)


def plot_metric(results, metric, ylabel, title, save_path):
    processed_items = [entry["processed_items"] for entry in results]
    values = [entry[metric] for entry in results]

    plt.figure(figsize=(8, 5))
    plt.plot(processed_items, values, marker="o", linestyle="-", markersize=3, label=metric)
    plt.xlabel("Number of Processed Items")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.savefig(save_path)
    plt.close()


def plot_percentile_category(results, category, save_path):
    processed_items = [entry["processed_items"] for entry in results]
    p50 = [entry["percentiles"][category].get("50th", 0.0) for entry in results]
    p90 = [entry["percentiles"][category].get("90th", 0.0) for entry in results]
    p95 = [entry["percentiles"][category].get("95th", 0.0) for entry in results]
    p100 = [entry["percentiles"][category].get("100th", 0.0) for entry in results]

    plt.figure(figsize=(8, 5))
    plt.plot(processed_items, p100, marker="*", linestyle=":", markersize=3, label="100th Percentile")
    plt.plot(processed_items, p95, marker="^", linestyle="-.", markersize=3, label="95th Percentile")
    plt.plot(processed_items, p90, marker="s", linestyle="-", markersize=3, label="90th Percentile")
    plt.plot(processed_items, p50, marker="o", linestyle="--", markersize=3, label="50th Percentile")

    plt.xlabel("Number of Processed Items")
    plt.ylabel("Error Value")
    plt.title(f"{category.capitalize()} Error Percentiles Over Time")
    plt.legend()
    plt.grid(True)

    plt.savefig(save_path)


def visualize(results_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    results = load_results(results_file)

    plot_metric(results, "avg_error", "Average Error", "Avg Error vs. Processed Items", f"{output_dir}/avg_error.png")
    plot_metric(results, "avg_error_percentage", "Average Error Percentage", "Avg Error Percentage vs. Processed Items", f"{output_dir}/avg_error_percentage.png")
    plot_metric(results, "overestimation_percentage", "Overestimation Percentage (%)", "Overestimation Percentage vs. Processed Items",
                f"{output_dir}/overestimation_percentage.png")
    plot_metric(results, "underestimation_percentage", "Underestimation Percentage (%)",
                "Underestimation Percentage vs. Processed Items",
                f"{output_dir}/underestimation_percentage.png")
    plot_metric(results, "exact_match_percentage", "Exact Match Percentage (%)",
                "Exact Match Percentage vs. Processed Items",
                f"{output_dir}/exact_match_percentage.png")
    plot_metric(results, "load_factor", "Load Factor", "Load Factor vs. Processed Items",
                f"{output_dir}/load_factor.png")
    plot_metric(results, "avg_query_time", "Average Query Time (seconds per item)", "Average Query Time vs. Processed Items",
                f"{output_dir}/avg_query_time.png")
    plot_metric(results, "memory_usage", "Memory Usage (bytes)", "Memory Usage vs. Processed Items",
                f"{output_dir}/memory_usage.png")
    plot_percentile_category(results, "overestimation", f"{output_dir}/overestimation_percentiles.png")
    plot_percentile_category(results, "underestimation", f"{output_dir}/underestimation_percentiles.png")
    plot_percentile_category(results, "combined", f"{output_dir}/combined_percentiles.png")
