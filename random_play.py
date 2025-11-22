import sys
import random

# Ensure that the library path is available
PW_PYTHON_PATH = "planet-wars-rts/app/src/main/python"
if PW_PYTHON_PATH not in sys.path:
    sys.path.insert(0, PW_PYTHON_PATH)

from agents.planet_wars_agent import PlanetWarsPlayer  # type: ignore
from core.game_state import Action  # type: ignore

def format_state(game_state):
        lines = []
        # Header
        lines.append(f"Tick: {game_state.game_tick}")
        # Totals per owner
        totals = {}
        for p in game_state.planets:
            key = getattr(p.owner, "value", str(p.owner))
            totals[key] = totals.get(key, 0.0) + float(p.n_ships)
        if totals:
            summary = " | ".join(f"{owner}: {int(total)}" for owner, total in totals.items())
            lines.append(f"Ships by owner -> {summary}")
        # Planet details
        lines.append("Planets:")
        lines.append("id\towner\tships\tgrowth\tr\tposX\tposY")
        for p in game_state.planets:
            owner = getattr(p.owner, "value", str(p.owner))
            lines.append(f"{p.id}\t{owner}\t{int(p.n_ships)}\t{p.growth_rate:.2f}\t{p.radius:.1f}\t{p.position.x:.1f}\t{p.position.y:.1f}")
        # Transports block
        lines.append("Transports:")
        lines.append("src\tdst\towner\tships\tx\ty")
        any_transit = False
        for p in game_state.planets:
            t = p.transporter
            if t is None:
                continue
            any_transit = True
            owner = getattr(t.owner, "value", str(t.owner))
            dest = getattr(t, "destination_index", getattr(t, "destination_planet_id", -1))
            lines.append(f"{p.id}\t{dest}\t{owner}\t{int(t.n_ships)}\t{t.s.x:.1f}\t{t.s.y:.1f}")
        if not any_transit:
            lines.append("(none)")
        return "\n".join(lines)

class RandomPlay(PlanetWarsPlayer):
    def get_action(self, game_state):
        # Get all the idle planets that are owned by the random player
        print(format_state(game_state))
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
