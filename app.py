from flask import Flask, render_template, request, jsonify
from models import db, Player, Stat, Match, Game, Variable, GamePlayer
from flask_cors import CORS
from datetime import datetime
from scheduleParse import getSchedule

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/roster")
def roster_page():
    return render_template("roster.html")


@app.route("/match")
def match_page():
    return render_template("match.html")




@app.route("/stats")
def stats_page():
    return render_template("stats.html")

from flask import request, jsonify
from models import Variable, db

from typing import Optional

def getVariable(varName: str):
    dbVar = Variable.query.filter_by(name=varName).first()
    return dbVar.value if dbVar else None

def setVariable(varName: str, value):
    dbVar = Variable.query.filter_by(name=varName).first()
    if not dbVar:
        dbVar = Variable(name=varName, value=str(value))
        db.session.add(dbVar)
    else:
        dbVar.value = str(value)
    db.session.commit()
    return dbVar.value

def getCurrentGameId() -> Optional[int]:
    current_game = Variable.query.filter_by(name="currentGame").first()

    if not current_game:
        current_match = Variable.query.filter_by(name="currentMatch").first()
        if not current_match:
            last_match = Match.query.order_by(Match.id.desc()).first()
            match_id = last_match.id if last_match else None
        else:
            match_id = int(current_match.value)

        last_game = Game.query.filter_by(match_id=match_id).order_by(Game.id.desc()).first()
        game_id = last_game.id if last_game else None
    else:
        game_id = int(current_game.value)

    return game_id

@app.route('/api/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    return jsonify({
        "id": game.id,
        "match_id": game.match_id,
        "game_number": game.game_number,
        "score": game.score,
        "score_opponent": game.score_opponent,
        "start_time": game.start_time.isoformat() if game.start_time else None,
        "end_time": game.end_time.isoformat() if game.end_time else None
    })




@app.route("/api/current", methods=["GET", "POST"])
def get_current():
    if request.method == "GET":
        current_match = Variable.query.filter_by(name="currentMatch").first()
        current_game = Variable.query.filter_by(name="currentGame").first()

        # Fallback to most recent match if variable not set
        if not current_match:
            last_match = Match.query.order_by(Match.id.desc()).first()
            match_id = last_match.id if last_match else None
        else:
            match_id = int(current_match.value)

        # Fallback to most recent game for that match
        if not current_game and match_id:
            last_game = Game.query.filter_by(match_id=match_id).order_by(Game.id.desc()).first()
            game_id = last_game.id if last_game else None
        else:
            game_id = int(current_game.value) if current_game else None

        return jsonify({
            "currentMatch": match_id,
            "currentGame": game_id
        })

    elif request.method == "POST":
        data = request.json
        match_id = data.get("currentMatch")
        game_id = data.get("currentGame")

        # Update or create currentMatch
        current_match = Variable.query.filter_by(name="currentMatch").first()
        if not current_match:
            current_match = Variable(name="currentMatch", value=str(match_id))
            db.session.add(current_match)
        else:
            current_match.value = str(match_id)

        # Update or create currentGame
        current_game = Variable.query.filter_by(name="currentGame").first()
        if not current_game:
            current_game = Variable(name="currentGame", value=str(game_id))
            db.session.add(current_game)
        else:
            current_game.value = str(game_id)

        db.session.commit()
        return jsonify({"message": "Updated current match/game"})

@app.route("/api/matches", methods=["GET"])
def get_matches():
    matches = Match.query.order_by(Match.date_time.desc()).all()
    return jsonify([
        {
            "id": m.id,
            "date_time": m.date_time.isoformat(),
            "court_number": m.court_number,
            "opponent": m.opponent
        } for m in matches
    ])


@app.route("/api/matches", methods=["POST"])
def create_match():
    data = request.json
    # Convert ISO 8601 string to datetime object
    date_time = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))

    match = Match(
        date_time=date_time,
        court_number=data["court_number"],
        opponent=data.get("opponent")
    )
    db.session.add(match)
    db.session.commit()
    return jsonify({"success": True, "match_id": match.id})

@app.route("/api/match/<int:match_id>/games", methods=["GET"])
def get_games_for_match(match_id):
    games = Game.query.filter_by(match_id=match_id).order_by(Game.game_number).all()
    return jsonify([
        {
            "game_number": g.game_number,
            "score": g.score,
            "score_opponent": g.score_opponent
        }
        for g in games
    ])

@app.route("/api/match/<int:match_id>/end", methods=["PUT"])
def end_match(match_id):
    match = Match.query.filter_by(id=match_id).first_or_404()

    data = request.get_json()
    date_time = datetime.fromisoformat(data["end_time"].replace("Z", "+00:00"))

    # Add this field to your Match model if it doesn't exist yet
    match.end_date_time = date_time

    db.session.commit()
    return jsonify({"message": "Match ended successfully."})


@app.route('/api/games', methods=['POST'])
def create_game():
    data = request.json
    new_game = Game(
        match_id=data['match_id'],
        game_number=data['game_number'],
        start_time=datetime.fromisoformat(data['start_time'].replace("Z", "+00:00"))
    )
    db.session.add(new_game)
    db.session.commit()
    return jsonify({
        "id": new_game.id,
        "match_id": new_game.match_id,
        "game_number": new_game.game_number,
        "start_time": new_game.start_time.isoformat()
    }), 201

@app.route('/api/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    data = request.json
    game = Game.query.get_or_404(game_id)

    if 'score' in data:
        game.score = data['score']
    if 'score_opponent' in data:
        game.score_opponent = data['score_opponent']
    if 'end_time' in data:
        game.end_time = datetime.fromisoformat(data['end_time'].replace("Z", "+00:00"))

    db.session.commit()
    return jsonify({"message": "Game updated successfully"}), 200

@app.route("/api/games/<int:game_id>/players", methods=["POST"])
def assign_players(game_id):
    game = Game.query.get_or_404(game_id)
    data = request.get_json()
    player_ids = data.get("players", [])

    # Remove existing player assignments for this game
    GamePlayer.query.filter_by(game_id=game_id).delete()

    # Add new player assignments
    for pid in player_ids:
        gp = GamePlayer(game_id=game_id, player_id=pid)
        db.session.add(gp)

    db.session.commit()
    return jsonify({"success": True})



@app.route("/api/players", methods=["GET", "POST"])
def players():
    if request.method == "POST":
        data = request.json
        name = data["name"]
        jersey = data.get("jersey")

        if jersey is None:
            # Auto-increment: find max jersey number used
            last_player = Player.query.order_by(Player.jersey.desc()).first()
            jersey = (
                (last_player.jersey + 1)
                if last_player and last_player.jersey is not None
                else 1
            )

        player = Player(name=name, jersey=jersey)
        db.session.add(player)
        db.session.commit()
        return jsonify(player.to_dict()), 201

    else:
        return jsonify([p.to_dict() for p in Player.query.all()])


@app.route("/api/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    player = Player.query.get(player_id)
    if player:
        db.session.delete(player)
        db.session.commit()
        return "", 204
    return "", 404

@app.route("/api/stats/<int:match_id>/<int:game_number>", methods=["GET"])
def get_game_stats(match_id, game_number):
    game = Game.query.filter_by(match_id=match_id, game_number=game_number).first()
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Ensure stats exist for all players in this game
    player_ids = [gp.player_id for gp in GamePlayer.query.filter_by(game_id=game.id)]
    existing_stats = {s.player_id: s for s in Stat.query.filter_by(game_id=game.id)}

    for pid in player_ids:
        if pid not in existing_stats:
            new_stat = Stat(player_id=pid, game_id=game.id)
            db.session.add(new_stat)
    db.session.commit()

    updated_stats = Stat.query.filter_by(game_id=game.id).all()
    return jsonify({s.player_id: s.to_dict() for s in updated_stats})



@app.route("/api/stats/<int:match_id>/<int:game_number>/<int:player_id>", methods=["GET", "POST"])
def update_stats(match_id, game_number, player_id):
    # Step 1: Find the Game
    game = Game.query.filter_by(match_id=match_id, game_number=game_number).first()
    if not game:
        return jsonify({"error": "Game not found"}), 404

    # Step 2: Query or create Stat for this player/game
    stat = Stat.query.filter_by(player_id=player_id, game_id=game.id).first()
    if not stat:
        stat = Stat(player_id=player_id, game_id=game.id)
        db.session.add(stat)
        db.session.commit()

    # Step 3: Handle stat updates
    if request.method == "POST":
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid or missing JSON"}), 400

        valid_fields = {
            "Ace", "ServiceError", "Kill", "AttackError", "Block",
            "Dig", "Assist", "Reception", "ReceptionError", "Touch"
        }

        for k, v in data.items():
            if k in valid_fields:
                try:
                    current = getattr(stat, k) or 0
                    setattr(stat, k, current + int(v))
                except (TypeError, ValueError):
                    return jsonify({"error": f"Invalid value for {k}"}), 400

        db.session.commit()

    return jsonify(stat.to_dict())

@app.route("/api/games/<int:game_id>/players", methods=["GET"])
def get_players_for_game(game_id):
    players = GamePlayer.query.filter_by(game_id=game_id).all()
    player_ids = [gp.player_id for gp in players]
    return jsonify(player_ids)


@app.route("/api/nextmatch", methods=["GET"])
def get_next_match():
    raw_team_id: str | None = request.args.get("team_id")
    team_id = int(raw_team_id) if raw_team_id is not None else None

    matches = getSchedule(team_id)  # should return a list of MatchItem or similar
    now = datetime.now()

    # Filter only matches in the future
    future_matches = [m for m in matches if (m.date_time and m.date_time > now)]

    # Sort by soonest date_time
    future_matches.sort(key=lambda m: m.date_time)

    next_match = future_matches[0] if future_matches else None

    if next_match:
        return jsonify(next_match.to_dict())  # Assuming MatchItem has a `to_dict()` method
    else:
        return jsonify(None)



@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify([s.to_dict() for s in Stat.query.all()])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
