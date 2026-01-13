from flask import Flask, jsonify, render_template
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog, leaguedashplayerstats
import pandas as pd
import random

app = Flask(__name__)

# 2024 DEFENSIVE RATINGS (Lower is better, but we use a multiplier)
# > 1.0 means Bad Defense (Good for scoring)
# < 1.0 means Good Defense (Bad for scoring)
DEFENSE_MULTIPLIERS = {
    'BOS': 0.92, 'MIN': 0.90, 'ORL': 0.93, 'OKC': 0.94, 'CLE': 0.95, # ELITE DEFENSES
    'LAL': 1.00, 'GSW': 1.00, 'MIA': 0.98, 'NYK': 0.97, 'PHI': 0.98, # MID
    'WAS': 1.10, 'DET': 1.08, 'SAS': 1.07, 'CHA': 1.09, 'ATL': 1.08, # BAD DEFENSES (Scoring Heaven)
    'UTA': 1.08, 'TOR': 1.06, 'MEM': 1.04, 'POR': 1.07, 'HOU': 0.99
}

def get_defense_factor(opponent_abbr):
    return DEFENSE_MULTIPLIERS.get(opponent_abbr, 1.00)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze/<name>')
def analyze(name):
    try:
        # 1. FIND PLAYER
        nba_players = players.get_players()
        player_list = [p for p in nba_players if p['full_name'].lower() == name.lower()]
        if not player_list: return {"error": "Player not found"}
        player_id = player_list[0]['id']
        
        # 2. GET DATA
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24')
        df = gamelog.get_data_frames()[0]
        if df.empty: return {"error": "No games found"}

        # 3. CALCULATE STATS
        last_5 = df.head(5)
        avg_pts = last_5['PTS'].mean()
        consistency = last_5['PTS'].std()
        
        # 4. OPPONENT LOGIC (Simulated for Demo)
        # In a real paid app, we would fetch the schedule. 
        # Here, we will pick a random opponent to demonstrate the logic.
        next_opponent = random.choice(list(DEFENSE_MULTIPLIERS.keys()))
        def_factor = get_defense_factor(next_opponent)
        
        # 5. FINAL PREDICTION
        # Formula: Average * Defense Factor
        projection = avg_pts * def_factor
        
        # Status Logic
        status = "OVER" if projection > avg_pts else "UNDER"

        return {
            "player": name.upper(),
            "projection": round(projection, 1),
            "avg_last_5": round(avg_pts, 1),
            "consistency": round(consistency, 1),
            "opponent": next_opponent,
            "opponent_rating": "WEAK DEFENSE" if def_factor > 1.02 else ("ELITE DEFENSE" if def_factor < 0.96 else "NEUTRAL"),
            "status": status,
            "last_game_pts": int(df.iloc[0]['PTS'])
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/top-props')
def top_props():
    # SIMULATED "TOP PROPS" DATA 
    # (Fetching live league leaders takes too long for a free user experience)
    top_picks = [
        {"name": "Luka Doncic", "prop": 32.5, "proj": 34.2, "team": "DAL", "confidence": "HIGH"},
        {"name": "Shai Gilgeous-Alexander", "prop": 30.5, "proj": 31.8, "team": "OKC", "confidence": "MED"},
        {"name": "Giannis Antetokounmpo", "prop": 29.5, "proj": 27.5, "team": "MIL", "confidence": "LOW"},
        {"name": "Jayson Tatum", "prop": 26.5, "proj": 28.1, "team": "BOS", "confidence": "HIGH"},
        {"name": "Tyrese Haliburton", "prop": 20.5, "proj": 22.4, "team": "IND", "confidence": "MED"}
    ]
    return jsonify(top_picks)

if __name__ == '__main__':
    app.run(debug=True)