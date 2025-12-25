"""Evolve the weights of a neural network using CMA-ES for the Planet Wars game."""

import sys
import cma
import os
import concurrent.futures as futures
import numpy as np
import torch
import torch.nn as nn
import sqlite3
from datetime import datetime

# Adding the python bindings of Planet Wars to the path
PW_PYTHON_PATH = "planet-wars-rts/app/src/main/python"
if PW_PYTHON_PATH not in sys.path:
    sys.path.insert(0, PW_PYTHON_PATH)

from core.game_state import Action  # type: ignore
from agents.planet_wars_agent import PlanetWarsPlayer  # type: ignore
from train_utils import *

class NeuralNetwork(nn.Module):
    """A neural network class for playing the Planet Wars game."""
    def __init__(self, input_dim, output_dim, hidden_sizes, solution=None):
        """Initialize the neural network for the given input and output dimensions"""
        super().__init__()
        layers = []  # A list for the layers of the neural network
        current_layer = input_dim  # The input dimension of the current layer
        for hidden_layer_size in hidden_sizes:  # For each hidden layer
            layers.append(nn.Linear(current_layer, hidden_layer_size))
            layers.append(nn.ReLU())
            current_layer = hidden_layer_size
        layers.append(nn.Linear(current_layer, output_dim))
        self.net = nn.Sequential(*layers)  # Create the neural network as a sequential model

        if solution is not None:
            self.set_model_weights(np.asarray(solution, dtype=np.float64))

    @torch.no_grad()
    def forward_outputs(self, flat_vec):
        """Forward pass through the neural network"""
        x = torch.from_numpy(flat_vec.astype(np.float32)).unsqueeze(0)  # Convert the flat vector to a tensor
        y = self.net(x).squeeze(0)  # Forward pass through the neural network
        noop_logits = float(y[0].item())
        planet_logits = y[1:-1].cpu().numpy().astype(np.float32)
        ship_ratio = float(torch.sigmoid(y[-1]).item())
        return noop_logits, planet_logits, ship_ratio

    def get_model_weights(self):
        """Returns a flat numpy array of all model weights and biases"""
        weights = []
        for param in self.parameters():  # Iterate through the parameters of the network
            weights.append(param.detach().cpu().numpy().reshape(-1))  # Add the parameters
        return np.concatenate(weights, axis=0)  # Merge them

    def set_model_weights(self, flat_weights):
        """Set the weights of the model that come from a flat numpy array"""
        prev_ind = 0
        for param in self.parameters():
            flat_size = param.numel()  # Get the parameter size
            new_vals = flat_weights[prev_ind:prev_ind + flat_size].reshape(param.shape)  # Reshape into the parameter size
            param.data.copy_(torch.from_numpy(new_vals).to(param.dtype))  # Copy the values to the parameter
            prev_ind += flat_size  # Update the index

class NeuralPlanetWarsAgent(PlanetWarsPlayer):
    """A neural network agent for playing the Planet Wars game"""
    def __init__(self, model):
        """Initialize the neural network agent with the given model"""
        super().__init__()
        self.model = model.eval()

    def get_action(self, game_state):
        """Get the next action using the game_state"""
        M = build_planet_matrix(game_state, self.params, self.player)  # Get the feature matrix
        flat_M = M.flatten().astype(np.float32)  # Flatten the feature matrix

        noop, logits, ratio = self.model.forward_outputs(flat_M)  # Pass it through the network

        # Find the idle planets that are owned by us. These planets can be used to send transporters. 
        idle_mine = [p for p in game_state.planets if p.owner == self.player and p.transporter is None]
        if not idle_mine:  # If there are no idle planets that are owned by us, then do nothing
            return Action.do_nothing()

        target_idx = int(np.argmax(logits))  # The ID of the target planet
        if noop >= float(logits[target_idx]):  # If the noop logit is higher than the logit of the target planet
            return Action.do_nothing()  # again do nothing

        # Find the source planet with the maximum number of ships
        source_planet = max(idle_mine, key=lambda p: float(p.n_ships))
        num_ships = int(float(source_planet.n_ships) * ratio)  # Determine the number of ships to send using the ratio
        if num_ships <= 0:  # If it is less than or equal to 0, do nothing
            return Action.do_nothing()
        dest = game_state.planets[target_idx]  # Use the destination planet given by the game state
        return Action(player_id=self.player,
                      source_planet_id=source_planet.id,
                      destination_planet_id=dest.id,
                      num_ships=num_ships)

    def get_agent_type(self) -> str:
        return "evolved_nn"

def train():
    input_dim = NUM_PLANETS * NUM_FEATURES  # Input dimensions for the network
    output_dim = NUM_PLANETS + 2  # We have 1 logit for the noop, 1 for each planet and 1 for ratio
    model = NeuralNetwork(input_dim, output_dim, HIDDEN_SIZES)  # The neural network model as the initial model
    theta0 = model.get_model_weights()  # Get the initial theta (which is random)

    es = cma.CMAEvolutionStrategy(theta0, SIGMA0)  # Start the CMA-ES
    
    # Prepare data directory and sqlite database
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite3")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS config (k TEXT PRIMARY KEY, v TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS results (generation INTEGER, individual INTEGER, fitness REAL, solution BLOB)")
    for k, v in cfg.items():
        cur.execute("INSERT OR REPLACE INTO config (k, v) VALUES (?, ?)", (str(k), str(v)))
    conn.commit()
    
    for gen in range(GENS):  # For each generation
        solutions = es.ask()  # Ask CMA-ES for solutions
        
        # For each solution, generate a task with the parameters
        models = [NeuralNetwork(input_dim, output_dim, HIDDEN_SIZES, np.asarray(sol, dtype=np.float64)) for sol in solutions]
        models = [NeuralPlanetWarsAgent(model) for model in models]
        tasks = [(model, NUM_PLANETS, GAMES_PER_EVAL, OPPONENT) for model in models]
        popsize = len(solutions)  # Number of individuals in the population
        
        cores = os.cpu_count() or 1
        capacity = WORKERS_PER_CORE * cores
        max_workers = popsize if popsize <= capacity else capacity
        
        with futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            losses_list = list(executor.map(evalute_individual, tasks))
        losses = [float(x) for x in losses_list]  # Get the losses
        es.tell(solutions, losses)  # Update the CMA-ES
        wins = [-l for l in losses]  # Get the real win ratios and other metrics
        gen_best = float(np.max(wins))
        gen_avg = float(np.mean(wins))
        print(f"GEN {gen+1}/{GENS}\tBest Win Ratio = {gen_best*100:.2f}%\t\tAverage Win Ratio = {gen_avg*100:.2f}%")
        
        # Save per-individual results
        for idx, sol in enumerate(solutions):
            fitness = float(wins[idx])
            solution_blob = np.asarray(sol, dtype=np.float64).tobytes()
            cur.execute(
                "INSERT INTO results (generation, individual, fitness, solution) VALUES (?, ?, ?, ?)",
                (int(gen), int(idx), fitness, sqlite3.Binary(solution_blob))
            )
        conn.commit()

    print("Training Completed!")
    conn.close()

if __name__ == "__main__":
    cfg = load_config()
    
    NUM_PLANETS = int(cfg["num_planets"])
    NUM_FEATURES = int(cfg["num_features"])
    HIDDEN_SIZES = list(cfg["hidden_sizes"])
    GAMES_PER_EVAL = int(cfg["games_per_eval"])
    GENS = int(cfg["gens"])
    SIGMA0 = float(cfg["sigma0"])
    OPPONENT = str(cfg["opponent"])
    WORKERS_PER_CORE = int(cfg["workers_per_core"])

    train()
