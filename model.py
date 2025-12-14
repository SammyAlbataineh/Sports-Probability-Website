import pandas as pd
import numpy as np 
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