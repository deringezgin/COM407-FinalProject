set -euo pipefail

MODE="${1:-}"

pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/planet-wars-rts/app/src/main/python"

pkill -f "client_server/game_agent_server.py" 2>/dev/null || true

python planet-wars-rts/app/src/main/python/client_server/game_agent_server.py &
sleep 5

cd planet-wars-rts
if [ "$MODE" = "headless" ]; then
  xvfb-run ./gradlew :app:runGUI
else
  ./gradlew :app:runGUI
fi
