import random
from typing import Optional

from agents.planet_wars_agent import PlanetWarsPlayer
from core.game_state import GameState, Action, Player, GameParams
from core.game_state_factory import GameStateFactory


import random
from typing import Optional

from agents.planet_wars_agent import PlanetWarsPlayer
from core.game_state import GameState, Action, Player, GameParams
from core.game_state_factory import GameStateFactory


class VanguardHeuristicAgent(PlanetWarsPlayer):
    def get_action(self, game_state: GameState) -> Action:
        best_action = Action.do_nothing()
        best_score = -9999.0

        my_planets = [p for p in game_state.planets if p.owner == self.player]
        enemy_planets = [p for p in game_state.planets if p.owner == self.player.opponent()]
        
        # Only issue orders from planets that aren't currently transporting
        ready_planets = [p for p in my_planets if p.transporter is None and p.n_ships > 5]

        if not ready_planets or not enemy_planets:
            return best_action

        # Identify our "Vanguard" (the friendly planet closest to any enemy planet)
        # This is the spearhead of our empire where we will funnel idle ships.
        vanguard_planet = None
        min_dist_to_enemy = float('inf')
        for p in my_planets:
            for e in enemy_planets:
                dist = p.position.distance(e.position)
                if dist < min_dist_to_enemy:
                    min_dist_to_enemy = dist
                    vanguard_planet = p

        for source in ready_planets:
            # --- 1. EVALUATE ATTACKS (EXPANSION & AGGRESSION) ---
            for target in game_state.planets:
                if target.owner == self.player:
                    continue 
                    
                dist = source.position.distance(target.position)
                eta = dist / self.params.transporter_speed
                
                if target.owner == Player.Neutral:
                    defense = target.n_ships
                    # Neutrals give economy, but don't actively hurt the enemy
                    strategic_value = target.growth_rate * 10
                else:
                    defense = target.n_ships + (target.growth_rate * eta)
                    # Double-swing value: +growth for us, AND -growth for them
                    strategic_value = target.growth_rate * 25 
                
                ships_needed = int(defense) + 3 # Tight +3 safety buffer
                
                if source.n_ships > ships_needed:
                    # Score heavily prioritizes valuable planets that are cheap to take
                    score = strategic_value / (ships_needed + (dist * 0.5) + 1)
                    
                    if score > best_score:
                        best_score = score
                        best_action = Action(
                            player_id=self.player,
                            source_planet_id=source.id,
                            destination_planet_id=target.id,
                            num_ships=ships_needed
                        )
            
            # --- 2. EVALUATE LOGISTICS (THE DEATHBALL) ---
            # If this planet is far from the action and has excess ships, 
            # funnel them to the Vanguard planet to reinforce the frontline.
            if vanguard_planet and source.id != vanguard_planet.id:
                dist_to_vanguard = source.position.distance(vanguard_planet.position)
                
                # Check if source is a safe "backline" planet 
                closest_enemy_dist = min(source.position.distance(e.position) for e in enemy_planets)
                
                # If we are safely out of reach and hoarding ships
                if closest_enemy_dist > min_dist_to_enemy * 1.5 and source.n_ships > 20:
                    
                    # Logistics score scales so that close, massive attacks override it, 
                    # but it easily beats wasting away doing nothing.
                    logistics_score = 8.0 / (dist_to_vanguard * 0.2 + 1) 
                    
                    if logistics_score > best_score:
                        best_score = logistics_score
                        # Leave a defensive garrison of 10, send the entire remainder to the front
                        best_action = Action(
                            player_id=self.player,
                            source_planet_id=source.id,
                            destination_planet_id=vanguard_planet.id,
                            num_ships=source.n_ships - 10
                        )

        return best_action

    def get_agent_type(self) -> str:
        return "Vanguard H. Agent"


class AdvancedHeuristicAgent(PlanetWarsPlayer):
    def get_action(self, game_state: GameState) -> Action:
        best_action = Action.do_nothing()
        best_score = -9999.0

        # Get all owned planets that are free to act
        my_planets = [p for p in game_state.planets 
                      if p.owner == self.player and p.transporter is None]
        
        # Get all planets we don't own
        candidate_targets = [p for p in game_state.planets if p.owner != self.player]

        if not my_planets or not candidate_targets:
            return best_action

        # Evaluate EVERY combination of our planets attacking EVERY target planet
        for source in my_planets:
            for target in candidate_targets:
                distance = source.position.distance(target.position)
                eta = distance / self.params.transporter_speed

                # 1. Estimate exact defense at ETA
                # Neutral planets usually do not grow ships over time
                if target.owner == Player.Neutral:
                    estimated_defense = target.n_ships
                else:
                    # Enemy planets will grow ships while our fleet is traveling
                    estimated_defense = target.n_ships + (target.growth_rate * eta)

                # 2. Calculate EXACT ships needed to capture (with a tiny +2 safety buffer)
                ships_needed = int(estimated_defense) + 2

                # 3. Only consider attacks we can actually afford while leaving a small 1-ship garrison
                if source.n_ships > ships_needed + 1 and ships_needed > 0:
                    
                    # 4. Calculate True ROI (Return on Investment)
                    # We want high growth rate, low ship cost, and low travel time
                    # Added +1 to the denominator to prevent division by zero
                    roi_score = target.growth_rate / (ships_needed + (distance * 0.2) + 1)
                    
                    # Bonus multiplier for attacking the enemy (steals their production)
                    if target.owner != Player.Neutral:
                        roi_score *= 1.5 

                    # Track the absolute most efficient move on the board
                    if roi_score > best_score:
                        best_score = roi_score
                        best_action = Action(
                            player_id=self.player,
                            source_planet_id=source.id,
                            destination_planet_id=target.id,
                            num_ships=ships_needed
                        )

        return best_action

    def get_agent_type(self) -> str:
        return "Advanced H. Agent"


# Example usage
if __name__ == "__main__":
    agent = AdvancedHeuristicAgent()
    agent.prepare_to_play_as(Player.Player1, GameParams())
    game_state = GameStateFactory(GameParams()).create_game()
    action = agent.get_action(game_state)
    print(action)