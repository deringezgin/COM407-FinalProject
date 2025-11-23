# Evolving a Neural-Network Agent for Planet Wars
[Project Website](https://sites.google.com/conncoll.edu/sharpcheedar)
[John Asaro](https://www.linkedin.com/in/johnmasaro/) - [Claire Carroll](https://www.linkedin.com/in/claire-carroll-204859329/) - [Derin Gezgin](https://www.linkedin.com/in/deringezgin/)

This repository includes our code for the final project of [COM407: Computational Intelligence](https://oak.conncoll.edu/parker/com407/index.html) course. In this final project, we evolved a simple neural network agent via CMA-ES for the Planet Wars game. 

## Setup

### Without Docker

Requirements: Python 3.10+, Java JDK 21, Git, Bash

```bash
git clone https://github.com/deringezgin/COM407-FinalProject
cd ci_final
./setup.sh
```

The setup script will create a Python virtual environment, clone the [Planet Wars source code](https://github.com/SimonLucas/planet-wars-rts), apply our patch for the GUI support, install the Python dependencies and build the Planet Wars app. 

If you already have your own virtual environment or wish not to have one, you can run the setup script with the `noenv` flag. 

```bash
./setup.sh noenv
```

### With Docker

You can also run our project in a Docker container.

```bash
git clone https://github.com/deringezgin/COM407-FinalProject
cd ci_final
docker build -t planet-wars-ci .
```

To run it with a GUI, start the container with display forwarding.

```bash
docker run -it -e DISPLAY=host.docker.internal:0 planet-wars-ci /bin/bash
```

If the display forwarding is not supported in your device, you can run our agent in headless mode described in the `Running the Trained Agent` section. 

## Training an Agent

To train a neural network agent, run the `train_nn.py` script. It is possible to specify a `.yaml` file with the `--config` flag. The default config is in `config1.yaml`.

```bash
python3 train_nn.py --config config1.yaml
```

The training script will scrape through the config file, evolve the network weights via CMA-ES and save the training progress (solution and fitness for each individual) and the used config into a timestamped SQLite database in the `data/` folder.

## Running the Trained Agent

To run the trained agent, first extract a solution from the training databases into a `.npy` file using `extract_agent.py` script:

```bash
python3 extract_agent.py
```

By default this script scans all `.sqlite3` databases in the `data/` folder, picks the best individual, and writes it to `sharp_agent_weights.npy` file. It is possible to specify a specific database, generation, individual, and output file via the `--db`, `--generation`, `--individual`, and `--outfile` flags.

### Running with GUI

After extracting the agent, simply run the `./run_sharp_agent.sh` script:

```bash
./run_sharp_agent.sh
```

This script will add the Planet Wars Python bindings to `PYTHONPATH`, acivate the `.venv` if it exists, restart the Python game server and run our trained agent against the greedy heuristic agent. 

### Running without a GUI

To evaluate the trained agent in headless mode, run the same script with the `headless` flag

```bash
./run_sharp_agent.sh headless
```

This runs the `run_agents.py` script to play a set of games between our trained agent against the greedy heuristic agent.

## Running Baseline Benchmarks

We also include a simple benchmarking script to compare the baseline agents. To run a benchmark and save the game results into a CSV file in the `benchmarks/` folder, use the `benchmarks/run_benchmark.py` script.

```bash
python3 benchmarks/run_benchmark.py --agent1 pure --agent2 greedy --n-games 100000
```

The script will run the requested number of games and write per‑game information (winner, planet counts, ship counts) to a .csv file. You can get a simple analysis of these outputs via the `benchmarks/analyze_benchmark.py` script. 

## Visualizing Results

After you complete the training and have a `.sqlite3` database in the `data/` folder, you can generate the fitness plot by running:

```bash
python3 plot_runs.py
```

The plot will be saved into the `plots` folder.
