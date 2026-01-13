from flask import Flask, jsonify, render_template
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import pandas as pd
import numpy as np

app = Flask(__name__)

def fetch_player_analysis(player_name):
    try:
        # 1. IDENTITY CHECK
        nba_players = players.get_players()
        player_list = [p for p in nba_players if p['full_name'].lower() == player_name.lower()]
        
        if not player_list:
            return {"error": "Player not found"}
        
        player_id = player_list[0]['id']
        
        # 2. DEEP DIVE DATA (Last 10 Games)
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24')
        df = gamelog.get_data_frames()[0]
        
        if df.empty:
             return {"error": "No games found"}

        # 3. ADVANCED FACTORS
        last_5 = df.head(5)
        avg_pts = last_5['PTS'].mean()
        consistency = last_5['PTS'].std() # Standard Deviation (Volatility)
        
        # Trend Factor: Is the player heating up?
        last_3_avg = df.head(3)['PTS'].mean()
        trend = "HEATING UP" if last_3_avg > avg_pts else "COOLING DOWN"

        # Home/Away Split (Simple Logic)
        # We check the most recent game to see if they were Home or Away
        last_game_matchup = df.iloc[0]['MATCHUP']
        is_home = "vs." in last_game_matchup # "vs" means Home, "@" means Away
        location_factor = "HOME ADVANTAGE" if is_home else "AWAY GAME"

        # 4. THE EXECUTOR (Prediction Logic)
        # If Home, add 5% to projection. If Away, subtract 5%.
        projection = avg_pts * 1.05 if is_home else avg_pts * 0.95

        return {
            "player": player_name.upper(),
            "projection": round(projection, 1),
            "avg_last_5": round(avg_pts, 1),
            "consistency": round(consistency, 1),
            "trend": trend,
            "location": location_factor,
            "status": "SAFE" if projection > 20 else "RISK",
            "last_game_pts": int(df.iloc[0]['PTS'])
        }

    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze/<name>')
def analyze(name):
    data = fetch_player_analysis(name)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)