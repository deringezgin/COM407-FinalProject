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
