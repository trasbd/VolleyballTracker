import requests
from bs4 import BeautifulSoup

from MatchItem import MatchItem

TEAM_ID = 7648
BASE_URL = "http://ds.oren.us/schedules/team_schedule.php?team="

def getSchedule(team_id: int | None = None) -> list[MatchItem]:
    if team_id is None:
        team_id = TEAM_ID  # Your default constant
    url = f"{BASE_URL}{team_id}"

    # Fetch the HTML page
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the schedule table
    matches_header = soup.find("h4", string="Matches")
    table = matches_header.find_next("table") if matches_header else None

    matches = []
    if table:
        rows = table.find_all("tr")[1:]  # Skip header row
        for row in rows:
            cols = [col.get_text(strip=True) for col in row.find_all("td")]
            if cols and len(cols) >= 5:
                # Create MatchItem
                match = MatchItem(
                    date_time_str=cols[0],
                    opponent=cols[2],
                    court=cols[3],
                    results=cols[4].replace("\n", " ").strip()
                )
                matches.append(match)

    return matches
