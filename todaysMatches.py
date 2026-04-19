import requests
from datetime import datetime, timedelta, timezone
ESPN_TO_MODEL = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "AFC Bournemouth",
    "AFC Bournemouth": "AFC Bournemouth",
    "Brentford": "Brentford",
    "Brighton & Hove Albion": "Brighton & Hove Albion",
    "Brighton and Hove Albion": "Brighton & Hove Albion",
    "Burnley": "Burnley",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Leeds United": "Leeds United",
    "Liverpool": "Liverpool",
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Newcastle United": "Newcastle United",
    "Nottingham Forest": "Nott'm Forest",
    "Sunderland": "Sunderland",
    "Tottenham Hotspur": "Tottenham Hotspur",
    "West Ham United": "West Ham United",
    "Wolverhampton Wanderers": "Wolves",
    # La Liga
    "Deportivo Alavés": "Alavés",
    "Alaves": "Alavés",
    "Athletic Club": "Athletic Bilbao",
    "Atletico Madrid": "Atlético Madrid",
    "Atlético de Madrid": "Atlético Madrid",
    "FC Barcelona": "Barcelona",
    "Barcelona": "Barcelona",
    "Celta de Vigo": "Celta Vigo",
    "Elche CF": "Elche",
    "RCD Espanyol": "Espanyol",
    "Getafe CF": "Getafe",
    "Girona FC": "Girona",
    "Levante UD": "Levante",
    "RCD Mallorca": "Mallorca",
    "CA Osasuna": "Osasuna",
    "Rayo Vallecano": "Rayo Vallecano",
    "Real Betis": "Real Betis",
    "Real Madrid": "Real Madrid",
    "Real Oviedo": "Real Oviedo",
    "Real Sociedad": "Real Sociedad",
    "Sevilla FC": "Sevilla",
    "Valencia CF": "Valencia",
    "Villarreal CF": "Villarreal",
    # Serie A
    "Atalanta": "Atalanta",
    "Bologna FC": "Bologna",
    "Cagliari Calcio": "Cagliari",
    "Cagliari": "Cagliari",
    "Como 1907": "Como",
    "US Cremonese": "Cremonese",
    "ACF Fiorentina": "Fiorentina",
    "Fiorentina": "Fiorentina",
    "Genoa CFC": "Genoa",
    "Hellas Verona": "Hellas Verona",
    "Inter Milan": "Milan",
    "Juventus": "Juventus",
    "SS Lazio": "Lazio",
    "Lazio": "Lazio",
    "US Lecce": "Lecce",
    "AC Milan": "AC Milan",
    "SSC Napoli": "Napoli",
    "Napoli": "Napoli",
    "Parma Calcio 1913": "Parma",
    "Pisa SC": "Pisa",
    "AS Roma": "Roma",
    "US Sassuolo": "Sassuolo",
    "Torino FC": "Torino",
    "Udinese Calcio": "Udinese",
    # Bundesliga
    "FC Augsburg": "Augsburg",
    "1. FC Union Berlin": "Union Berlin",
    "Werder Bremen": "Werder Bremen",
    "Borussia Dortmund": "Borussia Dortmund",
    "Eintracht Frankfurt": "Eintracht Frankfurt",
    "SC Freiburg": "Freiburg",
    "Hamburger SV": "Hamburger SV",
    "1. FC Heidenheim 1846": "Heidenheim",
    "TSG Hoffenheim": "Hoffenheim",
    "1. FC Köln": "Köln",
    "RB Leipzig": "RB Leipzig",
    "Bayer Leverkusen": "Bayer Leverkusen",
    "1. FSV Mainz 05": "Mainz 05",
    "Borussia Mönchengladbach": "Borussia Mönchengladbach",
    "FC Bayern Munich": "Bayern Munich",
    "FC St. Pauli": "St. Pauli",
    "VfB Stuttgart": "Stuttgart",
    "VfL Wolfsburg": "Wolfsburg",
    # Ligue 1
    "Angers SCO": "Angers",
    "AJ Auxerre": "Auxerre",
    "Stade Brestois 29": "Brest",
    "Le Havre AC": "Le Havre",
    "RC Lens": "Lens",
    "Lille OSC": "Lille",
    "FC Lorient": "Lorient",
    "Olympique Lyonnais": "Lyon",
    "Olympique de Marseille": "Marseille",
    "FC Metz": "Metz",
    "AS Monaco": "Monaco",
    "FC Nantes": "Nantes",
    "OGC Nice": "Nice",
    "Paris FC": "Paris FC",
    "Paris Saint-Germain": "Paris Saint-Germain",
    "Stade Rennais FC": "Rennes",
    "RC Strasbourg Alsace": "Strasbourg",
    "Toulouse FC": "Toulouse",
}
LEAGUE_SLUGS = {
    "EPL": "eng.1",
    "LaLiga": "esp.1",
    "Bundesliga": "ger.1",
    "SerieA": "ita.1",
    "Ligue1": "fra.1",
}
def _fetch_fixtures(league_key: str, days_ahead: int = 0, window: int = 1) -> list[dict]:
    slug = LEAGUE_SLUGS[league_key]
    base_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard"
    today = datetime.now(timezone.utc) + timedelta(days=days_ahead)
    end = today + timedelta(days=window)
    date_range = f"{today.strftime('%Y%m%d')}-{end.strftime('%Y%m%d')}"
    resp = requests.get(base_url, params={"dates": date_range}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    fixtures = []
    for event in data.get("events", []):
        comp = event["competitions"][0]
        home_espn = next(c for c in comp["competitors"] if c["homeAway"] == "home")["team"]["displayName"]
        away_espn = next(c for c in comp["competitors"] if c["homeAway"] == "away")["team"]["displayName"]
        home = ESPN_TO_MODEL.get(home_espn, home_espn)
        away = ESPN_TO_MODEL.get(away_espn, away_espn)
        status = event["status"]["type"]
        dt = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        fixtures.append({
            "Home": home,
            "Away": away,
            "HomeESPN": home_espn,
            "AwayESPN": away_espn,
            "League": league_key,
            "Date": dt,
            "Status": status["state"],
            "Detail": status["detail"],
            "Venue": comp.get("venue", {}).get("fullName", "N/A"),
        })
    return fixtures
def get_todays_matches() -> list[dict]:
    results = []
    for league in LEAGUE_SLUGS:
        try:
            results.extend(_fetch_fixtures(league, days_ahead=0, window=1))
        except Exception:
            pass
    return results
def get_upcoming_matches(days: int = 7) -> list[dict]:
    results = []
    for league in LEAGUE_SLUGS:
        try:
            results.extend(_fetch_fixtures(league, days_ahead=0, window=days))
        except Exception:
            pass
    results.sort(key=lambda x: x["Date"])
    return results