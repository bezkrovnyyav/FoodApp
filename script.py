#already done

import csv
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from models import Meal, Category


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stepik.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with open("delivery_categories.csv", "r") as f:
    reader = csv.DictReader(f, delimiter = ",")
    for i in reader:
        category = Category(id = int(i["id"]), title = i["title"])
        db.session.add(category)
        
with open("delivery_items.csv", "r") as f:
    reader = csv.DictReader(f, delimiter = ",")
    for i in reader:
        meal = Meal(id = int(i["id"]), title = i["title"], picture = i["picture"],
                description = i["description"], category_id = int(i["category_id"]),
                price = int(i["price"]))
        db.session.add(meal)
        
db.session.commit()