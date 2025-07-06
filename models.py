from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today)
    court_number = db.Column(db.Integer)
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


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    jersey = db.Column(db.Integer)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "jersey": self.jersey}

class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
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
            "Touch": self.Touch
        }
