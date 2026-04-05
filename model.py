import pandas as pd
import numpy as np
import math
import hashlib
import random

Pdf23=pd.read_csv("E0 (2).csv")
Pdf24=pd.read_csv("E0 (1).csv")
Pdf25=pd.read_csv("E0.csv")
Ldf23=pd.read_csv("season-2223.csv")
Ldf24=pd.read_csv("season-2324.csv")
Ldf25=pd.read_csv("season-2425.csv")
Ladf23=pd.read_csv("season-2223 (1).csv")
Ladf24=pd.read_csv("season-2324 (1).csv")
Ladf25=pd.read_csv("season-2425 (1).csv")
Iadf23=pd.read_csv("season-2223 (2).csv")
Iadf24=pd.read_csv("season-2324 (2).csv")
Iadf25=pd.read_csv("season-2425 (2).csv")
Badf23=pd.read_csv("season-2223 (3).csv")
Badf24=pd.read_csv("season-2324 (3).csv")
Badf25=pd.read_csv("season-2425 (3).csv")

league_dfs={
"EPL":pd.concat([Pdf23,Pdf24]),
"Ligue1":pd.concat([Ldf23,Ldf24]),
"LaLiga":pd.concat([Ladf23,Ladf24]),
"SerieA":pd.concat([Iadf23,Iadf24]),
"Bundesliga":pd.concat([Badf23,Badf24])
}

league_avgs={}
for league,df in league_dfs.items():
    df=df.copy()
    df["Date"]=pd.to_datetime(df["Date"],dayfirst=True,errors="coerce")
    df=df[df["Date"].dt.year<=2024]
    league_avgs[league]={"home_goals":df["FTHG"].mean(),"away_goals":df["FTAG"].mean()}

global_home_avg=np.mean([v["home_goals"] for v in league_avgs.values()])
global_away_avg=np.mean([v["away_goals"] for v in league_avgs.values()])

team_stats={}
for league,df in league_dfs.items():
    for _,row in df.iterrows():
        home_team=row["HomeTeam"]
        away_team=row["AwayTeam"]
        home_goals=row["FTHG"]
        away_goals=row["FTAG"]

        if home_team not in team_stats:
            team_stats[home_team]={"home_scored":0,"home_conceded":0,"away_scored":0,"away_conceded":0,"home_games":0,"away_games":0,"league":league}
        team_stats[home_team]["home_scored"]+=home_goals
        team_stats[home_team]["home_conceded"]+=away_goals
        team_stats[home_team]["home_games"]+=1

        if away_team not in team_stats:
            team_stats[away_team]={"home_scored":0,"home_conceded":0,"away_scored":0,"away_conceded":0,"home_games":0,"away_games":0,"league":league}
        team_stats[away_team]["away_scored"]+=away_goals
        team_stats[away_team]["away_conceded"]+=home_goals
        team_stats[away_team]["away_games"]+=1

team_strengths={}
for team,stats in team_stats.items():
    league=stats["league"]
    home_games=max(stats["home_games"],1)
    away_games=max(stats["away_games"],1)
    team_strengths[team]={
        "home_attack":(stats["home_scored"]/home_games)/league_avgs[league]["home_goals"],
        "home_defense":(stats["home_conceded"]/home_games)/league_avgs[league]["away_goals"],
        "away_attack":(stats["away_scored"]/away_games)/league_avgs[league]["away_goals"],
        "away_defense":(stats["away_conceded"]/away_games)/league_avgs[league]["home_goals"],
        "league":league
    }

def expected_goals(home_team,away_team):
    home_league=team_strengths[home_team]["league"]
    away_league=team_strengths[away_team]["league"]
    home_factor=league_avgs[home_league]["home_goals"]/global_home_avg
    away_factor=league_avgs[away_league]["away_goals"]/global_away_avg
    lambda_home=global_home_avg*team_strengths[home_team]["home_attack"]*team_strengths[away_team]["away_defense"]*home_factor
    lambda_away=global_away_avg*team_strengths[away_team]["away_attack"]*team_strengths[home_team]["home_defense"]*away_factor
    lambda_home=min(max(lambda_home,0.2),4.0)
    lambda_away=min(max(lambda_away,0.2),3.5)
    return lambda_home,lambda_away

def poisson(k,lam):
    return((lam**k)*np.exp(-lam))/math.factorial(k)

def generate_match_id(home,away,date):
    s=f"{home}-{away}-{date}"
    return int(hashlib.md5(s.encode()).hexdigest()[:8],16)

def match_probabilities(home_team,away_team,max_goals=5):
    lambda_home,lambda_away=expected_goals(home_team,away_team)
    home_win=0
    draw=0
    away_win=0
    for h in range(max_goals+1):
        for a in range(max_goals+1):
            prob=poisson(h,lambda_home)*poisson(a,lambda_away)
            if h>a:
                home_win+=prob
            elif h==a:
                draw+=prob
            else:
                away_win+=prob
    total=home_win+draw+away_win
    home_win/=total
    draw/=total
    away_win/=total
    idd=generate_match_id(home_team,away_team,"12/17/2025")
    return{"Home":home_team,"Away":away_team,"HomeWin":float(round(home_win*100,1)),"Draw":float(round(draw*100,1)),"AwayWin":float(round(away_win*100,1)),"Id":hash(idd)}