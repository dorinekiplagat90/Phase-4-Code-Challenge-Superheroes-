from flask import Flask, jsonify, request
from config import Config, db, migrate, mail
from models import Hero, Power, HeroPower
from flask_mail import Message

# ------------------------------
# Initialize Flask app & extensions
# ------------------------------
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
mail.init_app(app)

# ------------------------------
# ROUTES START HERE
# ------------------------------

# GET /heroes
@app.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()
    heroes_list = [hero.to_dict() for hero in heroes]
    return jsonify(heroes_list), 200

# GET /heroes/:id
@app.route("/heroes/<int:id>", methods=["GET"])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero:
        hero_dict = hero.to_dict()
        hero_dict["hero_powers"] = [hp.to_dict() for hp in hero.hero_powers]
        return jsonify(hero_dict), 200
    else:
        return jsonify({"error": "Hero not found"}), 404

# GET /powers
@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    powers_list = [power.to_dict() for power in powers]
    return jsonify(powers_list), 200

# GET /powers/:id
@app.route("/powers/<int:id>", methods=["GET"])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power:
        return jsonify(power.to_dict()), 200
    else:
        return jsonify({"error": "Power not found"}), 404

# PATCH /powers/:id
@app.route("/powers/<int:id>", methods=["PATCH"])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    description = data.get("description")

    try:
        power.description = description  # will trigger validation in model
        db.session.commit()
        return jsonify(power.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

# POST /hero_powers
@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json()
    hero_id = data.get("hero_id")
    power_id = data.get("power_id")
    strength = data.get("strength")

    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero or not power:
        return jsonify({"errors": ["Invalid hero_id or power_id"]}), 404

    try:
        hero_power = HeroPower(hero_id=hero_id, power_id=power_id, strength=strength)
        db.session.add(hero_power)
        db.session.commit()

        # Include nested hero and power in response
        response = hero_power.to_dict()
        response["hero"] = hero.to_dict()
        response["power"] = power.to_dict()
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": [str(e)]}), 400

# ------------------------------
# RUN APP
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
