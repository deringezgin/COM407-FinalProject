import numpy as np
from train_nn import NeuralNetwork, NeuralPlanetWarsAgent

AGENT_FILE = "sharp_agent_weights.npy"

def load_agent_data(data_file=AGENT_FILE):
    data = np.load(data_file, allow_pickle=True)
    data = data.item()
    return data

def build_agent(agent_dict):
    num_planets = int(agent_dict["num_planets"])
    num_features = int(agent_dict["num_features"])
    hidden_sizes = list(agent_dict["hidden_sizes"])
    weights = np.asarray(agent_dict["solution"], dtype=np.float64)

    input_dim = num_planets * num_features
    output_dim = num_planets + 2

    model = NeuralNetwork(input_dim, output_dim, hidden_sizes)
    model.set_model_weights(weights)
    return model

class SharpAgent(NeuralPlanetWarsAgent):
    def __init__(self, data_file=AGENT_FILE):
        agent_dict = load_agent_data(data_file)
        model = build_agent(agent_dict)
        super().__init__(model)
