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
def get_teams_from_csv(path):
    teams = set()
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            teams.add(row["HomeTeam"])
            teams.add(row["AwayTeam"])
    return teams
bundesliga_teams = get_teams_from_csv("season-2425 (3).csv")
serie_a_teams = get_teams_from_csv("season-2425 (2).csv")
la_liga_teams = get_teams_from_csv("season-2425 (1).csv")
ligue1_teams = get_teams_from_csv("season-2425.csv")
prem_teams = get_teams_from_csv("E0.csv")
df = pd.concat([Pdf23, Pdf24, Pdf25,Ldf23,Ldf24,Ldf25,Ladf23,Ladf24,Ladf25,Iadf23,Iadf24,Iadf25,Badf23,Badf24,Badf25], ignore_index=True)
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True,format="mixed",errors="coerce")
df = df.sort_values("Date").reset_index(drop=True)
train_df = df[df["Date"].dt.year <= 2024]
test_df  = df[df["Date"].dt.year == 2025]
teams = pd.concat([df["HomeTeam"], df["AwayTeam"]]).unique()
ratings = {team: 0.0 for team in teams}
BASE_MULT = 1.2
WIN_BONUS = 10
AWAY_BONUS = 8
GOAL_WEIGHT = 1.0
MIN_MULT = 1.0
REFERENCE_YEAR = 2025
REFERENCE_MONTH = 12
K = 0.002
D_MAX = 0.28
DRAW_SCALE = 400 
def recency_multiplier(match_date):
    months_ago = (REFERENCE_YEAR - match_date.year) * 12 + (REFERENCE_MONTH - match_date.month)
    mult = BASE_MULT - (months_ago / 10) - (months_ago / 12)
    return max(MIN_MULT, mult)
def add_val(goals_scored, won, away, date):
    val = goals_scored * GOAL_WEIGHT
    if won:
        val += WIN_BONUS
        if away:
            val += AWAY_BONUS
    mult = recency_multiplier(date)
    return val * mult
for _, row in train_df.iterrows():
    home_team = row["HomeTeam"]
    away_team = row["AwayTeam"]
    home_goals = row["FTHG"]
    away_goals = row["FTAG"]
    home_win = home_goals > away_goals
    away_win = away_goals > home_goals
    date = row["Date"]
    ratings[home_team] += add_val(home_goals, home_win, False, date)
    ratings[away_team] += add_val(away_goals, away_win, away_win, date)
total = 0
correct = 0
for _, row in test_df.iterrows():
    home = row["HomeTeam"]
    away = row["AwayTeam"]
    prediction = home if ratings[home] * BASE_MULT >= ratings[away] else away
    if row["FTHG"] != row["FTAG"]:
        actual = home if row["FTHG"] > row["FTAG"] else away
        if prediction == actual:
            correct += 1
        total += 1
    home_goals = row["FTHG"]
    away_goals = row["FTAG"]
    home_win = home_goals > away_goals
    away_win = away_goals > home_goals
    date = row["Date"]
    home_val = 0
    away_val = 0
    if ratings[home] > ratings[away]:
        if home_win:
            home_val = 5
    else:
        if away_win:
            away_val = 5
    ratings[home] += add_val(home_goals, home_win, False, date) + home_val
    ratings[away] += add_val(away_goals, away_win, away_win, date) + away_val
accuracy = (correct / total) * 100
print(f"Accuracy (no draws): {accuracy:.2f}%")
def sigmoid(x):
    return 1 / (1 + np.exp(-x))
def match_probabilities(home_rating, away_rating):
    diff = home_rating - away_rating
    abs_diff = abs(diff)
    p_draw = D_MAX * np.exp(-abs_diff / DRAW_SCALE)
    p_home_raw = sigmoid(K * diff)
    p_away_raw = 1 - p_home_raw
    remaining = 1 - p_draw
    p_home = remaining * p_home_raw
    p_away = remaining * p_away_raw
    return p_home, p_draw, p_away
def predict_match(home, away, ratings):
    p_home, p_draw, p_away = match_probabilities(
        ratings[home] * BASE_MULT,
        ratings[away]
    )
    return {
        "home": home,
        "away": away,
        "home_win": f"{round(p_home * 100, 1)}%",
        "draw": f"{round(p_draw * 100, 1)}%",
        "away_win": f"{round(p_away * 100, 1)}%",
        "prediction": (
            home if p_home >= p_draw and p_home >= p_away
            else "Draw" if p_draw >= p_home and p_draw >= p_away
            else away
        )
    }
def split_ratings_by_league(ratings, league_teams):
    return {team: ratings[team] for team in league_teams if team in ratings}
def normalize(league_ratings):
    mean = statistics.mean(league_ratings.values())
    normalized = {} 
    for team in league_ratings.keys():
        normalized[team] = league_ratings[team] / mean 
    return normalized
bundesliga_ratings = split_ratings_by_league(ratings, bundesliga_teams)
ligue1_ratings = split_ratings_by_league(ratings, ligue1_teams)
serie_a_ratings = split_ratings_by_league(ratings,serie_a_teams)
laliga_ratings = split_ratings_by_league(ratings, la_liga_teams)
prem_ratings = split_ratings_by_league(ratings,prem_teams)
bund_attack = normalize(bundesliga_ratings)
bund_defense = {team: 1 / value for team, value in bund_attack.items()}
la_attack = normalize(laliga_ratings)
la_defense = {team: 1 / value for team, value in la_attack.items()}
se_attack = normalize(serie_a_ratings)
se_defense = {team: 1 / value for team, value in se_attack.items()}
lig_attack = normalize(ligue1_ratings)
lig_defense = {team: 1 / value for team, value in lig_attack.items()}
prem_attack = normalize(prem_ratings)
prem_defense = {team: 1 / value for team, value in prem_attack.items()}
mu_home = {
    "EPL": 1.55,
    "Bundesliga": 1.60,
    "SerieA": 1.40,
    "LaLiga": 1.30,
    "Ligue1": 1.45
}
mu_away = {
    "EPL": 1.20,
    "Bundesliga": 1.30,
    "SerieA": 1.10,
    "LaLiga": 1.00,
    "Ligue1": 1.10
}
def expected_goals(home_team, away_team, league):
    if league == "EPL":
        attack = prem_attack
        defense = prem_defense
    elif league == "Bundesliga":
        attack = bund_attack
        defense = bund_defense
    elif league == "SerieA":
        attack = se_attack
        defense = se_defense
    elif league == "LaLiga":
        attack = la_attack
        defense = la_defense
    elif league == "Ligue1":
        attack = lig_attack
        defense = lig_defense
    else:
        raise ValueError("League not found")
    
    lambda_home = int(mu_home[league] * attack[home_team] * defense[away_team])
    lambda_away = int(mu_away[league] * attack[away_team] * defense[home_team])
    
    return lambda_home, lambda_away
def poisson(mu,lamb):
    return ((mu ** lamb) * np.exp(-1 * mu)) / math.factorial(lamb)
def match_probabilities(home_team,away_team,league,max_goals=5):
    lambda_home,lambda_away = expected_goals(home_team,away_team,league)
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
print(match_probabilities("Liverpool","Brighton","EPL"))