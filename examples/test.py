import time
from core.game_state import GameParams, Player
from core.game_state_factory import GameStateFactory
from core.forward_model import ForwardModel
from core.observation import ObservationFactory
from agents.random_agents import CarefulRandomAgent, PureRandomAgent
from agents.fully_observable_agent_adapter import as_unified
from agents.aggressive_agents import AggressiveStupidAgent, AggressiveNeutralAgent
def run_debug_loop():
    print("🌍 Initializing Step-by-Step Game...")
    
    # 1. Setup a small game (easier to read in the terminal)
    params = GameParams(num_planets=5, max_ticks=1000)
    
    # 2. Initialize the core engines
    factory = GameStateFactory(params)
    state = factory.create_game()
    forward_model = ForwardModel(state, params)
    
    # 3. Setup your agents
    agent1 = as_unified(AggressiveNeutralAgent())
    agent2 = as_unified(PureRandomAgent())

    agent1.prepare_to_play_as(Player.Player1, params)
    agent2.prepare_to_play_as(Player.Player2, params)

    # 4. THE GAME LOOP
    # We will manually step through the game until the max ticks are reached
    # (or until you add a break condition for when a player wins)
    while state.game_tick < params.max_ticks:
        print(f"\n" + "="*50)
        print(f"⏱️ TICK {state.game_tick}")
        print("="*50)

        # --- A. CUSTOMIZE YOUR DEBUG OUTPUT HERE ---
        # Let's see who owns what!
        p1_ships = sum(p.n_ships for p in state.planets if p.owner == Player.Player1)
        p2_ships = sum(p.n_ships for p in state.planets if p.owner == Player.Player2)
        print(f"📊 Fleet Totals -> Player 1: {p1_ships} ships | Player 2: {p2_ships} ships")
        
        for planet in state.planets:
            print(f"   Planet {planet.id}: Owner={planet.owner}, Ships={planet.n_ships}")

        # --- B. GENERATE OBSERVATIONS ---
        # Remember from the documentation: ObservationFactory takes a Set of observers
        obs1 = ObservationFactory.create(state, {Player.Player1})
        obs2 = ObservationFactory.create(state, {Player.Player2})

        # --- C. GET AGENT ACTIONS ---
        action1 = agent1.get_action(obs1)
        action2 = agent2.get_action(obs2)
        
        if action1: 
            print(f"🤖 Agent 1 moves: {action1}")
        if action2:
            print(f"🤖 Agent 2 moves: {action2}")

        # --- D. ADVANCE THE GAME PHYSICS ---
        # The forward model takes the current state and a dictionary of the actions, 
        # and returns the state for the next tick
        forward_model.step({
            Player.Player1: action1, 
            Player.Player2: action2
        })


        # --- E. PAUSE ---
        # Wait for you to press Enter before calculating the next tick. 
        # (Alternatively, use time.sleep(0.5) to let it auto-play slowly)
        input("\nPress [ENTER] to advance to the next tick...")

    print("\n🏁 Game Over!")

if __name__ == "__main__":
    run_debug_loop()