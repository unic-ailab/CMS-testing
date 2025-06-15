import os
import dash
import json
import datetime
import subprocess
from dash import dcc, html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import time


app = dash.Dash(__name__)
server = app.server

GRAPH_METRICS = [
    ("avg_error_graph", "avg_error", "Average Error", "Avg Error vs. Processed Items"),
    ("avg_error_percentage_graph", "avg_error_percentage", "Average Error Percentage", "Avg Error Percentage vs. Processed Items"),
    ("overestimation_percentage_graph", "overestimation_percentage", "Overestimation Percentage (%)", "Overestimation Percentage vs. Processed Items"),
    ("underestimation_percentage_graph", "underestimation_percentage", "Underestimation Percentage (%)", "Underestimation Percentage vs. Processed Items"),
    ("exact_match_percentage_graph", "exact_match_percentage", "Exact Match Percentage (%)", "Exact Match Percentage vs. Processed Items"),
    ("load_factor_graph", "load_factor", "Load Factor", "Load Factor vs. Processed Items"),
    ("avg_query_time_graph", "avg_query_time", "Average Query Time (seconds)", "Avg Query Time vs. Processed Items"),
    ("memory_usage_graph", "memory_usage", "Memory Usage (bytes)", "Memory Usage vs. Processed Items"),
]

PERCENTILE_GRAPHS = [
    ("overestimation_percentiles_graph", "overestimation"),
    ("underestimation_percentiles_graph", "underestimation"),
    ("combined_percentiles_graph", "combined"),
]

ALGORITHMS = ["CountMinSketch",
              "ConservativeCountMinSketch",
              "CountMeanMinSketch",
              "CountSketch",
              "SlidingCountMinSketch"]


app.layout = html.Div([
    html.Div([
        html.Label("Select Algorithm 1"),
        dcc.Dropdown(
            id='algo1-dropdown',
            options=[{'label': name, 'value': name} for name in ALGORITHMS],
            value='CountMinSketch'
        ),
        html.Br(),

        html.Label("Select Algorithm 2"),
        dcc.Dropdown(
            id='algo2-dropdown',
            options=[{'label': name, 'value': name} for name in ALGORITHMS],
            value='ConservativeCountMinSketch'
        ),
        html.Br(),

        html.Label("Width"),
        dcc.Input(id='width-input', type='number', value=10000, min=1),
        html.Br(),

        html.Label("Depth"),
        dcc.Input(id='depth-input', type='number', value=5, min=1),
        html.Br(),
        html.Br(),

        html.Label("Select a Dataset"),
        dcc.Dropdown(
            id='dataset-dropdown',
            options=[{'label': name, 'value': name} for name in [
                "FIFA.csv",
                "uchoice-Kosarak.txt",
                "uchoice-Kosarak-5-25.txt",
                "synthetic"
            ]],
            value='FIFA.csv'
        ),
        html.Br(),

        html.Button("Run Experiment", id='run-button', n_clicks=0,
                    style={'backgroundColor': 'green', 'color': 'white'},
                    disabled=False),

        html.Button("Stop Experiment", id='stop-button', n_clicks=0,
                    style={'backgroundColor': 'gray', 'color': 'white'}),
    ]),
    html.Div(id='graphs-container'),
    dcc.Interval(
        id='interval-component',
        interval=0.5 * 1000,
        n_intervals=0
    ),
    dcc.Store(id="latest-results-store"),
    dcc.Store(id="experiment-running-store", data=False),

])


def load_results(filepath, max_retries=3, delay=0.2):
    for attempt in range(max_retries):
        try:
            with open(filepath, "r") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"[Attempt {attempt + 1}/{max_retries}] JSON decode error in file '{filepath}': {e}")
        except FileNotFoundError:
            print(f"[Attempt {attempt + 1}/{max_retries}] File not found: '{filepath}'")
        except Exception as e:
            print(f"[Attempt {attempt + 1}/{max_retries}] Unexpected error with file '{filepath}': {e}")

        time.sleep(delay)

    print(f"Failed to load JSON after {max_retries} attempts: '{filepath}'")
    return None


def generate_line_graph(x, y, name, ylabel, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name=name))
    fig.update_layout(
        title=title,
        xaxis_title="Number of Processed Items",
        yaxis_title=ylabel,
        template="plotly_dark",
        height=400
    )
    return fig


def generate_metric_graph(results, metric, ylabel, title):
    x = [entry["processed_items"] for entry in results]
    y = [entry[metric] for entry in results]
    return generate_line_graph(x, y, metric, ylabel, title)


def generate_percentile_graph(results, category):
    x = [entry["processed_items"] for entry in results]
    get = lambda p: [entry["percentiles"][category].get(p, 0.0) for entry in results]
    percentiles = [("100th", get("100th")), ("95th", get("95th")),
                   ("90th", get("90th")), ("50th", get("50th"))]

    fig = go.Figure()
    for label, y in percentiles:
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name=f"{label} Percentile"))

    fig.update_layout(
        title=f"{category.capitalize()} Error Percentiles Over Time",
        xaxis_title="Number of Processed Items",
        yaxis_title="Error Value",
        template="plotly_dark",
        height=400
    )
    return fig


def get_result_path(algorithm, dataset, width, depth, timestamp):
    dir_path = f"../experiments/{dataset}/{algorithm}/w{width}_d{depth}/{timestamp}/results.json"
    return dir_path


@app.callback(
    Output('interval-component', 'disabled'),
    Output('latest-results-store', 'data'),
    Output('experiment-running-store', 'data', allow_duplicate=True),
    Input('run-button', 'n_clicks'),
    State('algo1-dropdown', 'value'),
    State('algo2-dropdown', 'value'),
    State('dataset-dropdown', 'value'),
    State('width-input', 'value'),
    State('depth-input', 'value'),
    prevent_initial_call='initial_duplicate'
)
def run_experiment(n_clicks, algo1, algo2, dataset, width, depth):
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate

    now = datetime.datetime.now()
    timestamp1 = now.strftime("%Y-%m-%d_%H-%M-%S")
    timestamp2 = (now + datetime.timedelta(seconds=1)).strftime("%Y-%m-%d_%H-%M-%S") if algo1 == algo2 else timestamp1

    proc1 = subprocess.Popen([
        "python3", "../simulation/simulation.py",
        "--algorithm", algo1,
        "--dataset", dataset,
        "--width", str(width),
        "--depth", str(depth),
        "--timestamp", timestamp1
    ])
    proc2 = subprocess.Popen([
        "python3", "../simulation/simulation.py",
        "--algorithm", algo2,
        "--dataset", dataset,
        "--width", str(width),
        "--depth", str(depth),
        "--timestamp", timestamp2
    ])

    results1 = get_result_path(algo1, dataset, width, depth, timestamp1)
    results2 = get_result_path(algo2, dataset, width, depth, timestamp2)

    return False, {
        algo1: {"path": results1, "pid": proc1.pid},
        algo2: {"path": results2, "pid": proc2.pid}
    }, True  # Mark experiment as running


@app.callback(
    Output('graphs-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('latest-results-store', 'data')
)
def update_graphs(n_intervals, results_paths):
    if not results_paths:
        return []

    data = {}
    for label, info in results_paths.items():
        path = info["path"] if isinstance(info, dict) else info
        if os.path.exists(path):
            loaded = load_results(path)
            if loaded:
                data[label] = loaded

    if not data:
        return []

    children = []

    # Graphs for scalar metrics
    for graph_id, metric, ylabel, title in GRAPH_METRICS:
        row = []
        for label in results_paths:
            if label in data:
                fig = generate_metric_graph(data[label], metric, ylabel, f"{title} [{label}]")
                row.append(html.Div(
                    dcc.Graph(id=f"{graph_id}-{label}", figure=fig),
                    style={"width": "50%", "display": "inline-block"}
                ))
        children.append(html.Div(row))

    # Graphs for percentiles
    for graph_id, category in PERCENTILE_GRAPHS:
        row = []
        for label in results_paths:
            if label in data:
                fig = generate_percentile_graph(data[label], category)
                fig.update_layout(title=f"{category.capitalize()} Percentiles [{label}]")
                row.append(html.Div(
                    dcc.Graph(id=f"{graph_id}-{label}", figure=fig),
                    style={"width": "50%", "display": "inline-block"}
                ))
        children.append(html.Div(row))

    return children


@app.callback(
    Output('interval-component', 'disabled', allow_duplicate=True),
    Output('experiment-running-store', 'data', allow_duplicate=True),
    Input('stop-button', 'n_clicks'),
    State('latest-results-store', 'data'),
    prevent_initial_call='initial_duplicate'
)
def stop_experiment(n_clicks, results_data):
    if not results_data:
        raise dash.exceptions.PreventUpdate

    for info in results_data.values():
        pid = info.get("pid")
        if pid:
            try:
                os.kill(pid, 9)  # 9 = SIGKILL (force kill)
            except OSError as e:
                print(f"Failed to kill process {pid}: {e}")
    return True, False  # Disable interval, mark experiment as not running


@app.callback(
    Output('run-button', 'disabled'),
    Output('run-button', 'style'),
    Input('experiment-running-store', 'data')
)
def toggle_run_button(is_running):
    if is_running:
        return True, {'backgroundColor': 'gray', 'color': 'white'}
    return False, {'backgroundColor': 'green', 'color': 'white'}


@app.callback(
    Output('stop-button', 'disabled'),
    Output('stop-button', 'style'),
    Input('experiment-running-store', 'data')
)
def toggle_stop_button(is_running):
    if is_running:
        return False, {'backgroundColor': 'red', 'color': 'white'}
    return True, {'backgroundColor': 'gray', 'color': 'white'}


if __name__ == '__main__':
    app.run(debug=True)
