import sys
import argparse
import csv
import os
import time

# Ensure Planet Wars Python bindings are on the path
PW_PYTHON_PATH = "planet-wars-rts/app/src/main/python"
if PW_PYTHON_PATH not in sys.path:
    sys.path.insert(0, PW_PYTHON_PATH)

from core.game_runner import GameRunner  # type: ignore
from core.game_state import GameParams, Player  # type: ignore
from agents.random_agents import PureRandomAgent, CarefulRandomAgent  # type: ignore
from agents.greedy_heuristic_agent import GreedyHeuristicAgent  # type: ignore

def parse_args():
    parser = argparse.ArgumentParser(description="Run benchmark games between random/greedy agents and save results to CSV.")
    parser.add_argument("--agent1", type=str, choices=["pure", "careful", "greedy"], default="pure", help="Type of agent 1: 'pure', 'careful', or 'greedy' (default: pure).")
    parser.add_argument("--agent2", type=str, choices=["pure", "careful", "greedy"], default="greedy", help="Type of agent 2: 'pure', 'careful', or 'greedy' (default: greedy).")
    parser.add_argument("--n-games", type=int, default=100000, help="Number of games to run (default: 100000)")
    parser.add_argument("--num-planets", type=int, default=12, help="Number of planets in the map (default: 12)")
    return parser.parse_args()

def main():
    args = parse_args()

    def make_agent(kind):
        if kind == "careful":
            return CarefulRandomAgent()
        if kind == "greedy":
            return GreedyHeuristicAgent()
        return PureRandomAgent()

    agent1 = make_agent(args.agent1)
    agent2 = make_agent(args.agent2)

    print(f"Benchmark: {agent1.get_agent_type()} vs {agent2.get_agent_type()}")
    print(f"Games: {args.n_games}, Num planets: {args.num_planets}")
    print("=" * 50)

    game_params = GameParams(num_planets=args.num_planets)
    runner = GameRunner(agent1, agent2, game_params)

    outfile = f"{args.agent1}_v_{args.agent2}_benchmark.csv"
    if not os.path.isabs(outfile):
        outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), outfile)

    start_time = time.time()

    with open(outfile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["game", "winner", "p1_planets", "p2_planets", "neutral_planets", "p1_ships", "p2_ships"])

        for i in range(1, args.n_games + 1):
            final_model = runner.run_game()
            winner = final_model.get_leader()

            planets = final_model.state.planets
            p1_planets = sum(1 for p in planets if p.owner == Player.Player1)
            p2_planets = sum(1 for p in planets if p.owner == Player.Player2)
            neutral_planets = sum(1 for p in planets if p.owner == Player.Neutral)

            p1_ships = final_model.get_ships(Player.Player1)
            p2_ships = final_model.get_ships(Player.Player2)

            writer.writerow([i, str(winner), p1_planets, p2_planets, neutral_planets, p1_ships, p2_ships])
            print(f"Game {i}/{args.n_games} winner: {winner} (P1 planets: {p1_planets}, "
                  f"P2 planets: {p2_planets}, Neutral: {neutral_planets}, "
                  f"P1 ships: {p1_ships:.1f}, P2 ships: {p2_ships:.1f})")

    time_diff = time.time() - start_time

    print("=" * 50)
    print(f"Results saved to {outfile}")
    print(f"Total time: {time_diff:.2f} seconds "
          f"({time_diff/args.n_games:.4f} s/game)")

if __name__ == "__main__":
    main()
