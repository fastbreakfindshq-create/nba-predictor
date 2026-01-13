from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

# 1. SETUP: Define who we want to track
target_player = "LeBron James"

def get_player_data(player_name):
    print(f"--- Searching for {player_name} ---")
    
    # Find the player's unique NBA ID
    nba_players = players.get_players()
    player = [p for p in nba_players if p['full_name'] == player_name]
    
    if not player:
        print("Player not found!")
        return
    
    player_id = player[0]['id']
    print(f"Found ID: {player_id}")

    # 2. FETCH: Get their recent game logs (Season 2024-25)
    # This pulls the actual stats from the NBA database
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25')
    
    # Convert to a readable DataFrame (Table)
    df = gamelog.get_data_frames()[0]
    
    # 3. ANALYZE: Show the last 5 games
    # We filter for specific columns: Game Date, Matchup, Minutes (MIN), Points (PTS)
    recent_games = df[['GAME_DATE', 'MATCHUP', 'MIN', 'PTS']].head(5)
    
    print("\nLast 5 Games Performance:")
    print(recent_games.to_string(index=False))

    # Simple Average Calculation
    avg_points = recent_games['PTS'].mean()
    print(f"\nAverage Points over last 5 games: {avg_points}")

# Run the function
if __name__ == "__main__":
    get_player_data(target_player)