import os
import sys

# Ensure library path from environment is available
PW_PYTHON_PATH = "planet-wars-rts/app/src/main/python"
if PW_PYTHON_PATH not in sys.path:
    sys.path.insert(0, PW_PYTHON_PATH)

from random_play import RandomPlay
from agents.random_agents import CarefulRandomAgent  # type: ignore
from core.game_runner import GameRunner  # type: ignore
from core.game_state import GameParams  # type: ignore
from core.forward_model import ForwardModel  # type: ignore

def main():
	# A minimal game setup with 10 planets
	game_params = GameParams(num_planets=10)

	# Our custom random agent v. the built-in random baseline
	agent1 = RandomPlay()
	agent2 = CarefulRandomAgent()
	runner = GameRunner(agent1, agent2, game_params)
	n_games = 10
	results = runner.run_games(n_games)

	print("Results (wins):", results)
	if ForwardModel.n_updates > 0:
		print(f"Successful actions: {ForwardModel.n_actions}")
		print(f"Failed actions: {ForwardModel.n_failed_actions}")

if __name__ == "__main__":
	main()
