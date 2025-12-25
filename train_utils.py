import numpy as np
import sys
import argparse
import os
import yaml
from core.game_state import GameState, GameParams, Player  # type: ignore
from core.game_runner import GameRunner  # type: ignore

# Adding the python bindings of Planet Wars to the path
PW_PYTHON_PATH = "planet-wars-rts/app/src/main/python"
if PW_PYTHON_PATH not in sys.path:
    sys.path.insert(0, PW_PYTHON_PATH)

def load_config():
    # Load config from the YAML file
    parser = argparse.ArgumentParser(description="Neural Evolver")
    parser.add_argument("--config", type=str, default="config1.yaml", help="Path to YAML config file")
    args = parser.parse_args()
    current_directory = os.path.dirname(__file__)
    CONFIG_PATH = args.config if os.path.isabs(args.config) else os.path.join(current_directory, args.config)
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg

def evalute_individual(args):
    # Unpack the arguments
    agent1, num_planets, games_per_eval, opponent_cls_path = args
    
    # Import the opponent agent
    mod_name, cls_name = opponent_cls_path.rsplit(".", 1)  
    opponent_mod = __import__(mod_name, fromlist=[cls_name])
    OpponentClass = getattr(opponent_mod, cls_name)
    wins = 0  # Keep track of the win count
    for _ in range(games_per_eval):
        agent2 = OpponentClass()  # Agent 2 is the opponent
        params = GameParams(num_planets=num_planets)
        runner = GameRunner(agent1, agent2, params)
        game_results = runner.run_game()  # Run the game
        if game_results.get_leader() == Player.Player1:  # Update the win count if we won
            wins += 1
    return -(wins / float(games_per_eval))  # Return the ratio of the number of games over the total

def build_planet_matrix(state: GameState, params: GameParams, me: Player) -> np.ndarray:
    """Build a matrix of features of the planets in the game state."""
    N = len(state.planets)  # Number of planets

    # The game dimensions
    game_width = params.width
    game_height = params.height

    # An array for the incoming ships to each planet
    incoming_friendly = np.zeros((N,), dtype=np.float32)
    incoming_enemy = np.zeros((N,), dtype=np.float32)

    for planet in state.planets:  # For each planet
        transporter = planet.transporter  # Transporter to destination planet
        if transporter is None:  # If there is no transporter, skip
            continue
        destination_planet = transporter.destination_index  # The destionation of the transporter

        # If the transporter is owned by me, add the ships to the incoming friendly array
        if transporter.owner == me:
            incoming_friendly[destination_planet] += float(transporter.n_ships)
        # If the transporter is owned by the opponent, add the ships to the incoming enemy array
        elif transporter.owner == me.opponent():
            incoming_enemy[destination_planet] += float(transporter.n_ships)

    F = 11
    M = np.zeros((N, F), dtype=np.float32)
    for i, p in enumerate(state.planets):
        tp = p.transporter
        if tp is not None:  # If there is a transporter, add the position and velocity information to the matrix
            tp_sx = float(tp.s.x) / game_width
            tp_sy = float(tp.s.y) / game_height
            tp_vx = float(tp.v.x) / float(params.transporter_speed)
            tp_vy = float(tp.v.y) / float(params.transporter_speed)
        else:  # If there is no transporter, set these values to 0.
            tp_sx = 0.0
            tp_sy = 0.0
            tp_vx = 0.0
            tp_vy = 0.0
        
        # Determine the owner of the planet
        if p.owner == me:
            owner_feature = 1
        elif p.owner == me.opponent():
            owner_feature = -1
        elif p.owner == Player.Neutral:
            owner_feature = 0
            
        M[i] = np.array(
            [
                owner_feature,
                min(1.0, float(p.n_ships) / 200.0),
                min(1.0, float(p.growth_rate) / float(params.max_growth_rate)),
                float(p.position.x) / game_width,
                float(p.position.y) / game_height,
                min(1.0, incoming_friendly[i] / 200.0),
                min(1.0, incoming_enemy[i] / 200.0),
                tp_sx, tp_sy,
                tp_vx, tp_vy,
            ],
            dtype=np.float32,
        )

    return M
