#!/usr/bin/env python3
"""
Round Robin Tournament Runner

This script pits a list of declared agents against each other in a Round Robin format.
Every agent plays every other agent. To eliminate spawn bias, each pairing plays
N games as Player 1 and N games as Player 2.
"""

import itertools
from core.game_state import GameParams, Player
from core.unified_game_runner import UnifiedGameRunner

# Import your agents
from agents.random_agents import PureRandomAgent, CarefulRandomAgent
from agents.greedy_heuristic_agent import GreedyHeuristicAgent
from agents.fully_observable_agent_adapter import as_unified
from agents.advanced_heuristic import AdvancedHeuristicAgent, VanguardHeuristicAgent
from agents.test_agents11 import TrainedMaskableGNNAgent
from agents.gnn_agent import AdvancedMaskableGNNAgent, EventDrivenGNNAgent, EventDrivenAllPlanetsGNNAgent, NoFrameSkipGNNAgent

def main():
    print("\n" + "=" * 70)
    print("PLANET WARS ROUND ROBIN TOURNAMENT")
    print("=" * 70)

    # =============================================================================
    # TOURNAMENT CONFIGURATION
    # =============================================================================
    
    # How many games per side? 
    # (e.g., 5 means A plays B 5 times as P1, and 5 times as P2 = 10 total games per matchup)
    GAMES_PER_SIDE = 25
    
    game_params = GameParams(num_planets=30, max_ticks=2000)

    # Declare all participants here. 
    # Format: {"name": "Readable Name", "agent": instantiated_agent}
    participants = [
        {
            "name": "Baseline", 
            "agent": as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/baseline.zip", det=True))
        },
        {
            "name": "Deep resGNN ", 
            "agent": as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/deep_resgnn_fixed30_planets.zip", det=True))
        },
        {
            "name": "Wide head",
            "agent": as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/wide_policy_30_planets.zip", det=True))
        },
        {
            "name": "Deep GNN",
            "agent": as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/deep_gnn_30_planets.zip", det=True))
        },
        {
            "name": "Deep ResGNN with handicap",
            "agent":as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/deep_resgnn_with_handicap_30_planets.zip", det=True))
        },
                {
            "name": "Deep GNN bigger Heads",
            "agent":as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/deep_gnn_2_30_planets.zip", det=True))
        },
        {
            "name": "Fast and Light", 
            "agent": as_unified(EventDrivenAllPlanetsGNNAgent(model_path="models/checkpoints/architecture_policies/fast_and_light_30_planets.zip", det=True))
        },
        {
            "name": "Careful Random", 
            "agent": as_unified(CarefulRandomAgent())
        },
        {
            "name": "Pure Random", 
            "agent": as_unified(PureRandomAgent())
        },
        {
            "name": "Greedy Heuristic", 
            "agent": as_unified(GreedyHeuristicAgent())
        },
        {
            "name": "Vanguard Heuristic",
            "agent": as_unified(VanguardHeuristicAgent())
        }
        # Add as many agents as you want here!
    ]

    # =============================================================================

    num_agents = len(participants)
    total_matchups = (num_agents * (num_agents - 1)) // 2
    games_per_matchup = GAMES_PER_SIDE * 2
    
    print(f"\n📊 Tournament Info:")
    print(f"   Participants:  {num_agents}")
    print(f"   Total Matchups: {total_matchups}")
    print(f"   Games/Matchup: {games_per_matchup} ({GAMES_PER_SIDE} as P1, {GAMES_PER_SIDE} as P2)")
    print(f"   Total Games:   {total_matchups * games_per_matchup}")
    print(f"   Map Size:      {game_params.num_planets} planets\n")

    # Initialize stats tracking
    leaderboard_stats = {
        p["name"]: {"wins": 0, "losses": 0, "games_played": 0} 
        for p in participants
    }

    # Generate all unique pairings
    matchups = list(itertools.combinations(participants, 2))

    print("=" * 70)
    print("STARTING MATCHES")
    print("=" * 70)

    for i, (p1, p2) in enumerate(matchups, 1):
        name1 = p1["name"]
        name2 = p2["name"]
        agent1 = p1["agent"]
        agent2 = p2["agent"]
        
        print(f"\nMatchup {i}/{total_matchups}: {name1} vs {name2}")
        
        # --- Leg 1: P1 is Player 1 ---
        runner_leg1 = UnifiedGameRunner(agent1, agent2, game_params, partial_observability=False)
        scores_leg1 = runner_leg1.run_games(GAMES_PER_SIDE)
        # --- Leg 2: P2 is Player 1 (Swap sides to prevent spawn bias) ---
        runner_leg2 = UnifiedGameRunner(agent2, agent1, game_params, partial_observability=False)
        scores_leg2 = runner_leg2.run_games(GAMES_PER_SIDE)

        # Aggregate Matchup Results
        p1_wins = scores_leg1[Player.Player1] + scores_leg2[Player.Player2]
        p2_wins = scores_leg1[Player.Player2] + scores_leg2[Player.Player1]

        print(f"   Result: {name1} ({p1_wins}) - ({p2_wins}) {name2}")

        # Update Leaderboard Stats
        leaderboard_stats[name1]["wins"] += p1_wins
        leaderboard_stats[name1]["losses"] += p2_wins
        leaderboard_stats[name1]["games_played"] += games_per_matchup

        leaderboard_stats[name2]["wins"] += p2_wins
        leaderboard_stats[name2]["losses"] += p1_wins
        leaderboard_stats[name2]["games_played"] += games_per_matchup

    # =============================================================================
    # LEADERBOARD GENERATION
    # =============================================================================
    
    print("\n" + "=" * 70)
    print("FINAL TOURNAMENT LEADERBOARD")
    print("=" * 70)

    # Calculate Win Rate and sort descending
    # Win Rate formula: Wins / Games Played
    def get_sort_key(stats):
        if stats["games_played"] == 0:
            return 0
        return stats["wins"] / stats["games_played"]

    # Sort participants based on the sort key (highest to lowest)
    sorted_standings = sorted(leaderboard_stats.items(), key=lambda item: get_sort_key(item[1]), reverse=True)

    # Print Table Header
    print(f"{'Rank':<5} | {'Agent Name':<28} | {'WR %':<7} | {'W-L':<10} | {'Total Games'}")
    print("-" * 70)

    # Print Rows
    for rank, (name, stats) in enumerate(sorted_standings, 1):
        wins = stats["wins"]
        losses = stats["losses"]
        total = stats["games_played"]
        
        wr_percentage = (get_sort_key(stats) * 100) if total > 0 else 0.0
        
        wld_str = f"{wins}-{losses}"
        print(f"{rank:<5} | {name:<28} | {wr_percentage:>5.1f}% | {wld_str:<10} | {total}")

    print("\nTournament Complete!\n")


if __name__ == "__main__":
    main()