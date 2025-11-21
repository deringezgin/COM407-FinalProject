import glob
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import scienceplots
plt.style.use(['science', 'no-latex'])

def read_generation_stats(db_path):
    connection = sqlite3.connect(db_path)  # Connect to the db
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT generation,
                   AVG(fitness) AS avg_fitness,
                   MAX(fitness) AS best_fitness
            FROM results
            GROUP BY generation
            ORDER BY generation
            """
        )
        # Get the generational data for each generation in the run
        rows = cursor.fetchall()
        generations = [int(r[0]) for r in rows]
        avg_fitness = [float(r[1]) for r in rows]
        best_fitness = [float(r[2]) for r in rows]
        return generations, avg_fitness, best_fitness
    finally:
        connection.close()  # At the end close the database connection

def read_run_config(db_path, key, default=""):
    connection = sqlite3.connect(db_path)
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT v FROM config WHERE k = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else default
    finally:
        connection.close()

def plot_run(db_path, output_dir):
    run_id = Path(db_path).stem
    layers = read_run_config(db_path, "hidden_sizes", "[]")
    games_per_individual = read_run_config(db_path, "games_per_eval", "")

    generations, avg_fitness, best_fitness = read_generation_stats(db_path)
    if not generations:
        return

    # Convert to percentages
    avg_pct = [x * 100.0 for x in avg_fitness]
    best_pct = [x * 100.0 for x in best_fitness]

    # Plot the run
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(generations, avg_pct, label="Average fitness", linewidth=2)
    ax.plot(generations, best_pct, label="Best fitness", linewidth=2)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Win Percentage")
    ax.set_ylim(0, 100)
    ax.set_title(f"Run: {run_id}, {layers} - {games_per_individual}")
    ax.legend()

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"run_{run_id}.png"
    fig.savefig(out_path, dpi=600, bbox_inches="tight")
    plt.close(fig)

def main():
    project_root_folder = Path(__file__).resolve().parent
    data_dir = project_root_folder / "data"
    plots_dir = project_root_folder / "plots"

    db_files = sorted(glob.glob(str(data_dir / "*.sqlite3")))
    for db_path in db_files:
        print("Processing:", db_path)
        plot_run(db_path, plots_dir)

if __name__ == "__main__":
    main()
