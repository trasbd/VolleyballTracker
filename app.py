from flask import Flask, render_template, request, jsonify
from models import db, Player, Stat
from flask_cors import CORS

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


@app.route("/api/stats/<int:player_id>", methods=["POST"])
def update_stats(player_id):
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    stat = Stat.query.filter_by(player_id=player_id).first()
    if not stat:
        stat = Stat(player_id=player_id)
        db.session.add(stat)

    for k, v in data.items():
        if hasattr(stat, k):
            current = getattr(stat, k) or 0  # <- default None to 0
            setattr(stat, k, current + v)

    db.session.commit()
    return jsonify(stat.to_dict())


@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify([s.to_dict() for s in Stat.query.all()])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
