set -euo pipefail

MODE="${1:-}"
echo "Adding the Python bindings to PYTHONPATH" 
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/planet-wars-rts/app/src/main/python"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

if [ "$MODE" = "headless" ]; then
  echo "Running the agents in the headless mode"
  python3 run_agents.py
else
  echo "Killing the existing server"
  pkill -f "client_server/game_agent_server.py" 2>/dev/null || true

  echo "Starting the new server"
  python3 planet-wars-rts/app/src/main/python/client_server/game_agent_server.py &
  sleep 5

  echo "Running the agents"
  cd planet-wars-rts
  ./gradlew :app:runGUI
fi
