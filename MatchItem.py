
from datetime import datetime
import re
from typing import Optional


class MatchItem:
    wins: int
    losses: int
    court: int
    def __init__(self, date_time_str: str, opponent: str, court: str, results: str):
        self.date_time: Optional[datetime] = self.parse_date(date_time_str)
        self.opponent: str = opponent
        self.courtString: str = court
        self.resultString: str = results
        self.parse_court()
        self.parse_results()

    def parse_date(self, s):
        try:
            return datetime.strptime(s, "%m/%d/%Y%I:%M %p")
        except Exception:
            return None
    
    def parse_court(self, courtString: Optional[str] = None):
        if(not courtString):
            courtString = self.courtString
        try:
            match = re.search(r"\d+", courtString)
            if match:
                self.court = int(match.group())
        except:
            self.court = None

    def parse_results(self, results: Optional[str] = None):
        if not results:
            results = self.resultString

        try:
            parts = results.split()
            self.wins = int(parts[1])
            self.losses = int(parts[3])
        except (IndexError, ValueError):
            self.wins = 0
            self.losses = 0  # fallback defaults

    def to_dict(self):
        return {
            "date_time": self.date_time.isoformat() if self.date_time else None,
            "opponent": self.opponent,
            "court": self.court,
            "wins": self.wins,
            "losses": self.losses,
            "resultString": self.resultString
        }

    def __repr__(self):
        return f"<MatchItem {self.date_time} vs {self.opponent} @ {self.court}>"