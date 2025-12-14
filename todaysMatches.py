import requests
from datetime import date
TEAM_NAME_MAP = {
    "Spurs": "Tottenham"
}
def get_todays_matches():
    fixtures = requests.get(
        "https://fantasy.premierleague.com/api/fixtures/"
    ).json()

    team_map = get_team_id_map()
    today = date.today().isoformat()

    matches = []
    for f in fixtures:
        if f["kickoff_time"] and f["kickoff_time"][:10] == today:
            matches.append({
                "home": team_map[f["team_h"]],
                "away": team_map[f["team_a"]]
            })
    for match in matches:
        if match["home"] in TEAM_NAME_MAP:
            match["home"] = TEAM_NAME_MAP[match["home"]]
        if match["away"] in TEAM_NAME_MAP:
            match["away"] = TEAM_NAME_MAP[match["away"]]
    return matches

def get_team_id_map():
    data = requests.get(
        "https://fantasy.premierleague.com/api/bootstrap-static/"
    ).json()

    return {
        team["id"]: team["name"]
        for team in data["teams"]
    }