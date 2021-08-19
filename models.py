from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stepik.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# db = SQLAlchemy()

orders_meals_association = db.Table(
    "orders_meals",
    db.Column("order_id", db.Integer, db.ForeignKey("orders.id")),
    db.Column("meal_id", db.Integer, db.ForeignKey("meals.id")))

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String)
    
    meals = db.relationship("Meal")

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.Date)
    summa = db.Column(db.Integer)
    status = db.Column(db.String)
    mail = db.Column(db.String)
    phone = db.Column(db.String)
    address = db.Column(db.String)
    
    #added to view value of meals in /account/ 
    json_order = db.Column(db.String)
    ###########
    
    user = db.relationship("User")
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    meals = db.relationship("Meal", secondary=orders_meals_association,
            back_populates="orders")

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    mail = db.Column(db.String)
    password = db.Column(db.String)
    orders = db.relationship("Order")

class Meal(db.Model):
    __tablename__ = "meals"
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String)
    price = db.Column(db.Integer)
    description = db.Column(db.String)
    picture = db.Column(db.String)
    category = db.relationship("Category")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    orders = db.relationship("Order", secondary=orders_meals_association,
            back_populates="meals")

db.create_all()
