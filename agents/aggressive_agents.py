import random
from typing import Optional

from agents.planet_wars_agent import PlanetWarsPlayer
from core.game_state import GameState, Action, Player, GameParams
from core.game_state_factory import GameStateFactory


class AggressiveStupidAgent(PlanetWarsPlayer):
    def get_action(self, game_state: GameState) -> Action:
        # Filter the planets owned by the player and without a transporter
        my_planets = [p for p in game_state.planets if p.owner == self.player and p.transporter is None]
        if not my_planets:
            return Action.do_nothing()

        # Filter opponent planets
        opponent_planets = [p for p in game_state.planets if p.owner == self.player.opponent()]
        if not opponent_planets:
            return Action.do_nothing()
        
        max_ships = -1
        planet_max = random.choice(my_planets)
        for i_planet in range(len(my_planets)):
            if my_planets[i_planet].n_ships > max_ships:
                max_ships = my_planets[i_planet].n_ships
                planet_max = my_planets[i_planet]

        source = planet_max
        target = random.choice(opponent_planets)

        return Action(
            player_id=self.player,
            source_planet_id=source.id,
            destination_planet_id=target.id,
            num_ships=source.n_ships 
        )

    def get_agent_type(self) -> str:
        return "Careful Random Agent"



class AggressiveNeutralAgent(PlanetWarsPlayer):
    def get_action(self, game_state: GameState) -> Action:
        # Filter the planets owned by the player and without a transporter
        my_planets = [p for p in game_state.planets if p.owner == self.player and p.transporter is None]
        if not my_planets:
            return Action.do_nothing()

        # Filter planets
        neutral_planets = [p for p in game_state.planets if p.owner == Player.Neutral]
        if not neutral_planets:
            opponent_planets = [p for p in game_state.planets if p.owner == self.player.opponent()]
            if not opponent_planets:
                return Action.do_nothing()
            planet_max = random.choice(my_planets)
            max_ships = planet_max.n_ships
            for i_planet in range(len(my_planets)):
                if my_planets[i_planet].n_ships > max_ships:
                    max_ships = my_planets[i_planet].n_ships
                    planet_max = my_planets[i_planet]

            planet_min = random.choice(opponent_planets)
            min_ships = planet_min.n_ships
            for i_planet in range(len(opponent_planets)):
                if opponent_planets[i_planet].n_ships < min_ships:
                    min_ships = opponent_planets[i_planet].n_ships
                    planet_min = opponent_planets[i_planet]
            if max_ships < 2 * min_ships:
                return Action.do_nothing()
            else:
                source = planet_max
                target = planet_min

        else:
            planet_max = random.choice(my_planets)
            max_ships = planet_max.n_ships
            for i_planet in range(len(my_planets)):
                if my_planets[i_planet].n_ships > max_ships:
                    max_ships = my_planets[i_planet].n_ships
                    planet_max = my_planets[i_planet]

            planet_min = random.choice(neutral_planets)
            min_ships = planet_min.n_ships
            for i_planet in range(len(neutral_planets)):
                if neutral_planets[i_planet].n_ships < min_ships:
                    min_ships = neutral_planets[i_planet].n_ships
                    planet_min = neutral_planets[i_planet]
            if max_ships < 2 * min_ships:
                return Action.do_nothing()
            else:
                source = planet_max
                target = planet_min

        return Action(
            player_id=self.player,
            source_planet_id=source.id,
            destination_planet_id=target.id,
            num_ships=source.n_ships/2 
        )

    def get_agent_type(self) -> str:
        return "Careful Random Agent"
