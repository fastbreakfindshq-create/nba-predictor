from flask import Flask, jsonify, render_template # Added render_template
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd

app = Flask(__name__)

# --- HELPER FUNCTION ---
def fetch_player_analysis(player_name):
    nba_players = players.get_players()
    player_list = [p for p in nba_players if p['full_name'].lower() == player_name.lower()]
    
    if not player_list:
        return {"error": "Player not found"}
    
    player_id = player_list[0]['id']
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2024-25')
    df = gamelog.get_data_frames()[0]
    
    # Safety Check: Ensure player has played games this season
    if df.empty:
         return {"error": "No games played this season"}

    recent_games = df[['GAME_DATE', 'MATCHUP', 'MIN', 'PTS']].head(5)
    avg_points = recent_games['PTS'].mean()
    
    return {
        "player": player_name,
        "average_pts_last_5": float(avg_points),
        "last_game_pts": int(recent_games.iloc[0]['PTS']),
        "status": "Safe" if avg_points > 25 else "Risky" # Adjusted threshold to 25
    }

# --- WEB ROUTES ---

@app.route('/')
def home():
    # This now looks inside the 'templates' folder for index.html
    return render_template('index.html') 

@app.route('/analyze/<name>')
def analyze(name):
    data = fetch_player_analysis(name)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)