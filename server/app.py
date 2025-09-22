#!/usr/bin/env python3
import os
from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Restaurant, RestaurantPizza, Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def restaurants():
    restaurants = Restaurant.query.all()
    res_list = [r.to_dict() for r in restaurants]
    return make_response(res_list, 200)


@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def restaurants_by_id(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if not restaurant:
        return {"error": "Restaurant not found"}, 404

    if request.method == "GET":
        return make_response(
            restaurant.to_dict(
                only=("id", "name", "address", "restaurant_pizzas")
            ),
            200,
        )

    if request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204



@app.route("/pizzas", methods=["GET"])
def pizzas():
    pizzas = Pizza.query.all()
    pizza_list = [p.to_dict() for p in pizzas]
    return make_response(pizza_list, 200)


@app.route("/restaurant_pizzas", methods=["POST"])
def restaurant_pizzas():
    data = request.get_json()

    try:
        new_rp = RestaurantPizza(
            price=data["price"],
            restaurant_id=data["restaurant_id"],
            pizza_id=data["pizza_id"],
        )
        db.session.add(new_rp)
        db.session.commit()
        return new_rp.to_dict(), 201
    except ValueError:
        return {"errors": ["validation errors"]}, 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
