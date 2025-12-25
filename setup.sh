set -euo pipefail

PLANET_WARS_REPO="https://github.com/SimonLucas/planet-wars-rts.git"
REPO_DIR="planet-wars-rts"
PATCH_FILE="planet-wars-rts-addGUI.patch"

echo "Checking the Java version..."
if ! java -version 2>&1 | grep -qE '\"21\.'; then
  echo "Error: Java 21 is required."
  echo "Detected Java version is:"
  java -version
  exit 1
fi
echo "Java 21 detected"

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
python3 -m pip install -r requirements.txt

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
