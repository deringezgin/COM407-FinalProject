set -euo pipefail

MODE="${1:-}"
ENV_NAME="planetenv"

echo "Adding the Python bindings to PYTHONPATH"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/planet-wars-rts/app/src/main/python"

command -v conda >/dev/null 2>&1 || { echo "Error: conda not found (run ./setup.sh after installing Miniconda/Anaconda)."; exit 1; }

if [ "$MODE" = "headless" ]; then
  echo "Running the agents in the headless mode"
  conda run -n "$ENV_NAME" python3 run_agents.py
else
  echo "Killing the existing server"
  pkill -f "client_server/game_agent_server.py" 2>/dev/null || true

  echo "Starting the new server"
  conda run -n "$ENV_NAME" python3 planet-wars-rts/app/src/main/python/client_server/game_agent_server.py &
  
  echo "Waiting for server on ws://localhost:8765..."
  for i in {1..30}; do
    if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
      echo "Server is running!"
      break
    fi
    sleep 1
    echo "Server is not running..."
  done

  echo "Running the agents"
  cd planet-wars-rts
  ./gradlew :app:runGUI
fi
