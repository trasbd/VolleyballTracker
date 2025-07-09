from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

import json

class Variable(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)

    def set_value(self, val):
        self.value = json.dumps(val)

    def get_value(self):
        return json.loads(self.value)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=date.today)
    end_date_time = db.Column(db.DateTime)
    court_number = db.Column(db.Integer)
    opponent = db.Column(db.String(100))
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"))

    games = db.relationship("Game", backref="match", lazy=True)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer)
    score_opponent = db.Column(db.Integer) 
    game_number = db.Column(db.Integer)
    side = db.Column(db.String(50))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))

    stats = db.relationship("Stat", backref="game", lazy=True)
    positions = db.relationship('GamePosition', backref='game', lazy=True)

class GamePosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    slot = db.Column(db.Integer)  # optional: to store position order (e.g., 1 to 6)

    position = db.relationship("Position")

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))  # e.g., "Setter", "Libero", "OH1", "MB2"

class GamePlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)



class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    jersey = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

    def to_dict(self):
        return {"id": self.id, "name": self.name, "jersey": self.jersey}

class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    position_start = db.Column(db.Integer, db.ForeignKey('position.id'))
    position_end = db.Column(db.Integer, db.ForeignKey('position.id'))
    Ace = db.Column(db.Integer, default=0)
    ServiceError = db.Column(db.Integer, default=0)
    Kill = db.Column(db.Integer, default=0)
    AttackError = db.Column(db.Integer, default=0)
    Block = db.Column(db.Integer, default=0)
    Dig = db.Column(db.Integer, default=0)
    Assist = db.Column(db.Integer, default=0)
    Reception = db.Column(db.Integer, default=0)
    ReceptionError = db.Column(db.Integer, default=0)
    Touch = db.Column(db.Integer, default=0)
    Saves = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "Ace": self.Ace,
            "ServiceError": self.ServiceError,
            "Kill": self.Kill,
            "AttackError": self.AttackError,
            "Block": self.Block,
            "Dig": self.Dig,
            "Assist": self.Assist,
            "Reception": self.Reception,
            "ReceptionError": self.ReceptionError,
            "Touch": self.Touch,
            "Saves": self.Saves
        }
