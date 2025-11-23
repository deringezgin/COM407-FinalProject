# Evolving a Neural-Network Agent for Planet Wars
`John Asaro - Claire Carroll - Derin Gezgin`

This repository includes our code for the final project of COM407: Computational Intelligence course. In this final project, we evolved a simple neural network agent via CMA-ES for the Planet Wars game. 

## Setup

### Without Docker

Requirements: Python 3.10+, Java JDK 21, Git, Bash

```bash
git clone https://github.com/deringezgin/COM407-FinalProject
cd ci_final
./setup.sh
```

The setup script will create a Python virtual environment, clone the [Planet Wars source code](https://github.com/SimonLucas/planet-wars-rts), apply our patch for GUI support, install the Python dependencies and build the Planet Wars app. 

If you would already have your own virtual environment or wish not to have one, you can run the setup script with the `noenv` flag. 

```bash
bash setup.sh noenv
```
