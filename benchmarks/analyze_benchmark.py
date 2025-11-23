import os
import pandas as pd

def analyze_file(csv_path):
    df = pd.read_csv(csv_path)

    # Win counts
    winners = df["winner"].value_counts().to_dict()
    total_games = int(df.shape[0])

    metrics = ["p1_planets", "p2_planets", "neutral_planets", "p1_ships", "p2_ships"]  # Other metrics
    stats = {}
    for col in metrics:
        series = df[col]
        stats[col] = (series.mean(), series.std(ddof=1))  # Calculate the mean and st.dev.

    return winners, stats, total_games

def format_report(csv_path, winners, stats, total_games):
    lines = []

    filename = os.path.basename(csv_path)
    stem, _ = os.path.splitext(filename)
    base = stem[: -len("_benchmark")]
    parts = base.split("_v_", 1)
    player1 = parts[0]
    player2 = parts[1]

    lines.append(f"Benchmark analysis for: {filename}")
    lines.append("=" * 60)
    lines.append(f"Player 1: {player1}")
    lines.append(f"Player 2: {player2}")
    lines.append("")
    lines.append(f"Total games: {total_games}")
    lines.append("")

    lines.append("Win counts:")
    for winner, count in sorted(winners.items(), key=lambda x: (-x[1], x[0])):
        pct = (count / total_games * 100.0) if total_games > 0 else 0.0
        lines.append(f"{winner:20s} {count:8d} ({pct:6.2f}%)")

    lines.append("")

    lines.append("Aggregate stats (all games):")
    header = f"{'Metric':20s} {'Mean':>12s} {'StdDev':>12s}"
    lines.append(header)
    lines.append("-" * len(header))

    metric_order = ["p1_planets", "p2_planets", "neutral_planets", "p1_ships", "p2_ships"]

    for metric in metric_order:
        mean, stdev = stats.get(metric, (float("nan"), float("nan")))
        lines.append(f"{metric:20s} {mean:12.3f} {stdev:12.3f}")

    lines.append("")
    return "\n".join(lines)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Get all the benchmark results
    csv_files = [os.path.join(base_dir, name) for name in os.listdir(base_dir) if name.endswith("_benchmark.csv")]

    if not csv_files:
        print("No *_benchmark.csv files found to analyze.")
        return

    for csv_path in csv_files:  # For each csv file
        winners, stats, total_games = analyze_file(csv_path)  # Run analysis
        report = format_report(csv_path, winners, stats, total_games)  # Create report

        filename = os.path.basename(csv_path)
        stem, _ = os.path.splitext(filename)
        out_name = f"{stem}_analysis.txt"
        out_path = os.path.join(base_dir, out_name)
        with open(out_path, "w") as f: f.write(report)

if __name__ == "__main__":
    main()
