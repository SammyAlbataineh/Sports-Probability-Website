import requests
from datetime import datetime, timedelta, timezone


def _fetch_fixtures(league_slug: str) -> list[dict]:
    """Generic fetcher for any ESPN soccer league slug."""
    base_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league_slug}/scoreboard"
    
    today = datetime.now(timezone.utc)
    week_later = today + timedelta(days=7)
    date_range = f"{today.strftime('%Y%m%d')}-{week_later.strftime('%Y%m%d')}"
    
    response = requests.get(base_url, params={"dates": date_range})
    response.raise_for_status()
    data = response.json()
    
    fixtures = []
    for event in data.get("events", []):
        comp = event["competitions"][0]
        home = next(c for c in comp["competitors"] if c["homeAway"] == "home")
        away = next(c for c in comp["competitors"] if c["homeAway"] == "away")
        status = event["status"]["type"]
        dt = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        
        fixtures.append({
            "league":  data["leagues"][0]["name"],
            "date":    dt,
            "home":    home["team"]["displayName"],
            "away":    away["team"]["displayName"],
            "status":  status["state"],    # pre / in / post
            "detail":  status["detail"],   # kick-off time or match minute
            "venue":   comp.get("venue", {}).get("fullName", "N/A"),
        })
    
    return fixtures


def get_premier_league():
    """English Premier League"""
    return _fetch_fixtures("eng.1")


def get_la_liga():
    """Spanish La Liga"""
    return _fetch_fixtures("esp.1")


def get_bundesliga():
    """German Bundesliga"""
    return _fetch_fixtures("ger.1")


def get_serie_a():
    """Italian Serie A"""
    return _fetch_fixtures("ita.1")


def get_ligue_1():
    """French Ligue 1"""
    return _fetch_fixtures("fra.1")


def print_fixtures(fixtures: list[dict]):
    if not fixtures:
        print("  No fixtures found.\n")
        return
    
    league_name = fixtures[0]["league"]
    print(f"\n{'=' * 90}")
    print(f"  {league_name}")
    print(f"{'=' * 90}")
    print(f"  {'Date':<18} {'Home':<28} {'Away':<28} {'Status'}")
    print(f"  {'-' * 85}")
    
    for g in fixtures:
        local = g["date"].astimezone()
        date_str = local.strftime("%a %b %d %H:%M")
        print(f"  {date_str:<18} {g['home']:<28} {g['away']:<28} {g['detail']}")


if __name__ == "__main__":
    leagues = [
        get_premier_league,
        get_la_liga,
        get_bundesliga,
        get_serie_a,
        get_ligue_1,
    ]
    
    for fn in leagues:
        try:
            fixtures = fn()
            print_fixtures(fixtures)
        except Exception as e:
            print(f"Error fetching {fn.__name__}: {e}")