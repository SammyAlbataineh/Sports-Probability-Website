import pandas as pd
import numpy as np 
import math 
import statistics
import csv 
Pdf23 = pd.read_csv("E0 (2).csv")
Pdf24 = pd.read_csv("E0 (1).csv")
Pdf25 = pd.read_csv("E0.csv")
Ldf23 = pd.read_csv("season-2223.csv")
Ldf24 = pd.read_csv("season-2324.csv")
Ldf25 = pd.read_csv("season-2425.csv")
Ladf23 = pd.read_csv("season-2223 (1).csv")
Ladf24 = pd.read_csv("season-2324 (1).csv")
Ladf25 = pd.read_csv("season-2425 (1).csv")
Iadf23 = pd.read_csv("season-2223 (2).csv")
Iadf24 = pd.read_csv("season-2324 (2).csv")
Iadf25 = pd.read_csv("season-2425 (2).csv")
Badf23 = pd.read_csv("season-2223 (3).csv")
Badf24 = pd.read_csv("season-2324 (3).csv")
Badf25 = pd.read_csv("season-2425 (3).csv")
league_dfs = {
    "EPL": pd.concat([Pdf23, Pdf24]),
    "Ligue1": pd.concat([Ldf23, Ldf24]),
    "LaLiga": pd.concat([Ladf23, Ladf24]),
    "SerieA": pd.concat([Iadf23, Iadf24]),
    "Bundesliga": pd.concat([Badf23, Badf24])
}
mu_home = {}
mu_away = {}
for league, ldf in league_dfs.items():
    ldf = ldf.copy()
    ldf["Date"] = pd.to_datetime(ldf["Date"], dayfirst=True, errors="coerce")
    ldf = ldf[ldf["Date"].dt.year <= 2024]
    mu_home[league] = ldf["FTHG"].mean()
    mu_away[league] = ldf["FTAG"].mean()
team_stats = {} 
for league in league_dfs.keys():
    for _,row in league_dfs[league].iterrows():
        home_team = row["HomeTeam"]
        away_team = row["AwayTeam"]
        home_goals = row["FTHG"]
        away_goals = row["FTAG"]
        if home_team not in team_stats:
            team_stats[home_team] = {
                "home_scored": home_goals,
                "home_conceded": away_goals,
                "away_scored": 0,
                "away_conceded": 0,
                "home_games": 1,
                "away_games": 0,
                "league": league
            }
        else:
            team_stats[home_team]["home_scored"] += home_goals 
            team_stats[home_team]["home_conceded"] += away_goals 
            team_stats[home_team]["home_games"] += 1 
        if away_team not in team_stats:
            team_stats[away_team] = {
                "home_scored": 0,
                "home_conceded": 0,
                "away_scored": away_goals,
                "away_conceded": home_goals,
                "home_games": 0,
                "away_games": 1,
                "league": league
            }
        else:
            team_stats[away_team]["away_scored"] += away_goals
            team_stats[away_team]["away_conceded"] += home_goals  
            team_stats[away_team]["away_games"] += 1 
league_avgs = {}
for league, df in league_dfs.items():
    league_avgs[league] = {
        "home_goals": df["FTHG"].mean(),
        "away_goals": df["FTAG"].mean()
    }
team_strengths = {}
for team, stats in team_stats.items():
    league = stats["league"]
    home_games = max(stats["home_games"], 1)
    away_games = max(stats["away_games"], 1)
    team_strengths[team] = {
        "home_attack":
            (stats["home_scored"] / home_games) /
            league_avgs[league]["home_goals"],

        "home_defense":
            (stats["home_conceded"] / home_games) /
            league_avgs[league]["away_goals"],

        "away_attack":
            (stats["away_scored"] / away_games) /
            league_avgs[league]["away_goals"],

        "away_defense":
            (stats["away_conceded"] / away_games) /
            league_avgs[league]["home_goals"],

        "league": league
    }
    
def expected_goals(home_team, away_team):
    league = team_strengths[home_team]["league"]
    lambda_home = (
        league_avgs[league]["home_goals"] *
        team_strengths[home_team]["home_attack"] *
        team_strengths[away_team]["away_defense"]
    )

    lambda_away = (
        league_avgs[league]["away_goals"] *
        team_strengths[away_team]["away_attack"] *
        team_strengths[home_team]["home_defense"]
    )
    lambda_home = min(max(lambda_home, 0.2), 4.0)
    lambda_away = min(max(lambda_away, 0.2), 3.5)
    return lambda_home,lambda_away
def poisson(k, lam):
    return ((lam ** k) * np.exp(-lam)) / math.factorial(k)
def match_probabilities(home_team,away_team,max_goals=5):
    lambda_home,lambda_away = expected_goals(home_team,away_team)
    home_win = 0
    draw = 0
    away_win = 0
    for h in range(max_goals+1):
        for a in range(max_goals+1):
            prob = poisson(h, lambda_home) * poisson(a, lambda_away)
            if h > a:
                home_win += prob
            elif h == a:
                draw += prob
            else:
                away_win += prob
    total = home_win + draw + away_win
    home_win /= total
    draw /= total
    away_win /= total
    return {"Home Win": float(round(home_win * 100,2)), "Draw": float(round(draw * 100,2)), "Away Win": float(round(away_win * 100,2))}
