set -euo pipefail

MODE="${1:-}"

PLANET_WARS_REPO="https://github.com/SimonLucas/planet-wars-rts.git"
REPO_DIR="planet-wars-rts"
PATCH_FILE="planet-wars-rts-addGUI.patch"

if [ "$MODE" != "noenv" ]; then
  echo "Creating the virtual environment"
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
  fi
fi

echo "Setting up the Planet Wars repository"

if [[ ! -f "$PATCH_FILE" ]]; then
  echo "Patch file '$PATCH_FILE' not found in $(pwd)"
  exit 1
fi

if [[ -d "$REPO_DIR" ]]; then
  echo "The repository is already cloned"
else
  echo "Cloning $PLANET_WARS_REPO..."
  git clone "$PLANET_WARS_REPO" "$REPO_DIR"
fi

echo "Installing the Python dependencies..."
pip install -r requirements.txt

echo "Adding the Python bindings to PYTHONPATH" 
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/planet-wars-rts/app/src/main/python"

cd "$REPO_DIR"
echo "Applying patch '../$PATCH_FILE'..."
git apply "../$PATCH_FILE"
echo "Patch applied successfully."

echo "Building the App..."
./gradlew :app:build -x test
echo "App build done!"

echo "\n"

echo "To run the Sharp Agent against the Greedy heuristic agent, run:"
echo "'./gradlew :app:runGUI' inside the repository"
