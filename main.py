
import requests
import json
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')


def get_today_matches():

    url = f"https://app.footystats.org/app-todays-matches?key=pattystats2&tz=WAT&division=leagues&date={today}"

    headers = {
        "User-Agent": "dart"
    }

    response = requests.get(url, headers=headers)
    data = response.json()['data']
    matches = []

    for match in data:
        for m in match['matches']:
            match_info = {
                "id": m['id'],
                "heure": datetime.fromtimestamp(m['date_unix']).strftime('%H:%M:%S'),
                "league": match['title'],
                "pays": match['country'],
                "team_a": m['home_name'],
                "team_b": m['away_name']
            }
            matches.append(match_info)
    matches.sort(key=lambda x: x['heure'])
    with open("matches.json", "w", encoding='utf-8') as file:
        json.dump(matches, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    get_today_matches()
