import argparse
import ast
import glob
import os
import sqlite3
import numpy as np

def load_config(cur):
    # Fetch all the config table
    cur.execute("SELECT k, v FROM config")
    cfg = {str(k): str(v) for (k, v) in cur.fetchall()}
    return cfg

def pick_row(cur, generation, individual):
    # If both the generation and individual is specified, directly select it
    if generation is not None and individual is not None:
        cur.execute(
            "SELECT generation, individual, fitness, solution "
            "FROM results WHERE generation = ? AND individual = ? "
            "LIMIT 1",
            (int(generation), int(individual)),
        )
    
    # If the individual is not specified, return the best individual in the generation
    elif generation is not None:
        cur.execute(
            "SELECT generation, individual, fitness, solution "
            "FROM results WHERE generation = ? "
            "ORDER BY fitness DESC LIMIT 1",
            (int(generation),),
        )
    
    # If nothing is specified, return the best overall individual
    else:
        cur.execute(
            "SELECT generation, individual, fitness, solution "
            "FROM results ORDER BY fitness DESC LIMIT 1"
        )

    row = cur.fetchone()  # Fetch the row
    if row is None: raise RuntimeError("No matching row found in results table")
    return row

def best_from_db(db_path, generation, individual):
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cfg = load_config(cur)  # Load the config of the database

        try:
            # Scrape the crucial config components
            num_planets = int(cfg["num_planets"])
            num_features = int(cfg["num_features"])
            hidden_sizes = list(ast.literal_eval(cfg["hidden_sizes"]))
        except KeyError as e:
            raise RuntimeError(f"Missing config key {e} in {db_path!r}")

        # Scrape the individual
        _, _, fitness, solution = pick_row(cur, generation, individual)
        weights = np.frombuffer(solution, dtype=np.float64)

        agent_dict = {
            "num_planets": num_planets,
            "num_features": num_features,
            "hidden_sizes": list(hidden_sizes),
            "solution": weights,
        }
        return agent_dict, float(fitness)
    finally:
        conn.close()

def main():
    # Command Line arguments to control what to extract
    parser = argparse.ArgumentParser(description="Extract an individual from training databases into a .npy file.")
    parser.add_argument("--db", type=str, help="Path to a specific SQLite DB (default: search in db-folder).")
    parser.add_argument("--db-folder", type=str, default="data", help="Folder containing SQLite DBs (default: ./data).")
    parser.add_argument("--generation", type=int, help="Generation index to select within the DB.")
    parser.add_argument("--individual", type=int, help="Individual index to select within the generation.")
    parser.add_argument("--outfile", type=str, default="sharp_agent_weights.npy", help="Output .npy file (default: sharp_agent_weights.npy).")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))  # Project directory
    db_folder = os.path.join(base_dir, args.db_folder)  # Folder that has the databases

    generation = args.generation
    individual = args.individual

    # If generation/individual are set without a database, this is not possible
    # Or if there is only individual, it is not possible
    if args.db is None and (generation is not None or individual is not None):
        raise SystemExit("--generation/--individual require --db to be specified.")

    # If a specific db is provided
    if args.db is not None:
        db_path = os.path.join(db_folder, args.db)
        if not os.path.exists(db_path): raise SystemExit(f"DB file not found: {db_path}")

        agent_dict, fitness = best_from_db(db_path, generation, individual)
        np.save(os.path.join(base_dir, args.outfile), agent_dict)
        print(f"Wrote individual from {db_path} (fitness={fitness:.2f}) to {args.outfile}")
        return

    # If no database is specified, find the overall best
    db_paths = sorted(glob.glob(os.path.join(db_folder, "*.sqlite3")))
    if not db_paths: raise SystemExit(f"No .sqlite3 databases found in {db_folder!r}")

    best_fitness = float("-inf")
    best_agent = None
    best_db = None

    for db_path in db_paths:
        try:
            agent_dict, fitness = best_from_db(db_path, None, None)
        except Exception as e:
            print(f"Skipping {db_path}: {e}")
            continue
        if fitness > best_fitness:
            best_fitness = fitness
            best_agent = agent_dict
            best_db = db_path

    if best_agent is None: raise SystemExit("No valid individuals found in any database.")

    np.save(os.path.join(base_dir, args.outfile), agent_dict)
    print(f"Wrote best overall individual from {best_db} (fitness={best_fitness:.4f}) to {args.outfile}")

if __name__ == "__main__":
    main()
