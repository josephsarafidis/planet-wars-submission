#!/usr/bin/env python3
"""
Simplest example: Battle two local Python agents (no containers needed).

This demonstrates the core game-playing logic without needing to:
- Clone repositories
- Build containers
- Launch servers

Perfect for quick testing and learning the basics.
"""

from core.game_state import GameParams
from core.unified_game_runner import UnifiedGameRunner
from agents.random_agents import PureRandomAgent, CarefulRandomAgent
from agents.greedy_heuristic_agent import GreedyHeuristicAgent
from agents.fully_observable_agent_adapter import as_unified
from agents.system2_agents import HardcodedCommander
from agents.aggressive_agents import AggressiveStupidAgent, AggressiveNeutralAgent
from agents.gnn_agent import AdvancedMaskableGNNAgent, EventDrivenGNNAgent, EventDrivenAllPlanetsGNNAgent


from agents.test_agents11 import TrainedMaskableGNNAgent


from agents.system2_agents import GNNCommanderAgent, GoNoGoAgent
from agents.random_commander import RandomCommanderAgent
from agents.test_agent import SpatialGNNAgent
from agents.advanced_heuristic import AdvancedHeuristicAgent, VanguardHeuristicAgent

def main():
    """Run a quick battle between local Python agents."""

    print("\n" + "=" * 70)
    print("LOCAL PYTHON AGENT BATTLE")
    print("=" * 70)

    # =============================================================================
    # CUSTOMIZE THESE - Choose any two local Python agents
    # =============================================================================

    #agent1 = as_unified(GNNAgent(model_path="app/src/main/python/training/gnn_planet_wars_agent.zip"))
    


    agent1 = as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/deep_resgnn_30_planets.zip"))
    agent2 = as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/deep_resgnn_fixed30_planets.zip"))

    #models/checkpoints/planetwars_selfplay_event_driven_champion_30planets.zip
    #agent2 = as_unified(TrainedMaskableGNNAgent(model_path=f"models/league/rl_gen_10.zip"))


    agent1_name = agent1.get_agent_type()
    agent2_name = agent2.get_agent_type()

    n_games = 20
    game_params = GameParams(num_planets=26, max_ticks=2000)

    # =============================================================================

    print(f"\n🤖 Agent 1: {agent1_name}")
    print(f"🤖 Agent 2: {agent2_name}")
    print(f"🎮 Games: {n_games}")
    print(f"🌍 Planets: {game_params.num_planets}")
    print(f"⏱️  Max ticks: {game_params.max_ticks}")

    # Create runners for both fully and partially observable modes
    print("\n" + "=" * 70)
    print("FULLY OBSERVABLE MODE")
    print("=" * 70)

    runner_full = UnifiedGameRunner(
        agent1, agent2, game_params,
        partial_observability=False
    )

    print(f"\n🎮 Playing {n_games} games...")
    scores_full = runner_full.run_games(n_games)

    from core.game_state import Player

    print(f"\n📊 Results (Fully Observable):")
    print(f"   {agent1_name} (Player1): {scores_full[Player.Player1]} wins")
    print(f"   {agent2_name} (Player2): {scores_full[Player.Player2]} wins")
    if scores_full[Player.Neutral] > 0:
        print(f"   Draws: {scores_full[Player.Neutral]}")

   

    # Compare the modes
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    print(f"\nHow observability affects the agents:")
    print(f"  Fully Observable:     {agent1_name} won {scores_full[Player.Player1]}/{n_games}")

    print("\n✨ Done!\n")


if __name__ == "__main__":
    main()
