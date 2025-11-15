import sys
import random

# Ensure that the library path is available
PW_PYTHON_PATH = "planet-wars-rts/app/src/main/python"
if PW_PYTHON_PATH not in sys.path:
    sys.path.insert(0, PW_PYTHON_PATH)

from agents.planet_wars_agent import PlanetWarsPlayer  # type: ignore
from core.game_state import Action  # type: ignore

class RandomPlay(PlanetWarsPlayer):
    def get_action(self, game_state):
        # Get all the idle planets that are owned by the random player
        idle_planets = [p for p in game_state.planets if p.owner == self.player and p.transporter is None]
        if not idle_planets:  # If no idle planets, do nothing
            return Action.do_nothing()

		# Among all the idle planets, pick a random source
        source = random.choice(idle_planets)
        
        # Pick a random target among all planets (including mine, neutral, or opponent)
        target = random.choice(game_state.planets)

        num_ships = source.n_ships / 2
        if num_ships <= 0:
            return Action.do_nothing()
        return Action(
			player_id=self.player,
			source_planet_id=source.id,
			destination_planet_id=target.id,
			num_ships=num_ships
		)
    
    def get_agent_type(self):
         return "random_agent"
