from flask import Flask, render_template, request, session, redirect, url_for
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import *
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from random import shuffle
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stepik.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "super_secret_random_string"
db = SQLAlchemy(app)
migrate = Migrate(app, db) # needed?
admin = Admin(app)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Order, db.session))
admin.add_view(ModelView(Meal, db.session))

def inside_cart():
    if not session.get("cart"):
        return None
    else:
        total = 0
        tmp = json.loads(session["cart"])
        for i in tmp.items(): 
            total += Meal.query.filter(Meal.id == int(i[0])).first().price * int(i[1])
        return (sum(tmp.values()), total)

def get_id():
    user_id = ""
    if session.get("user_id"):
        user_id = str(session["user_id"])
    return user_id
        
def get_cart():
    cart = inside_cart()
    if not cart:
        cart = "Пуста"
    else:
        cart = "{} блюда {}руб.".format(cart[0], cart[1])
    return cart
        
@app.route("/")
def first():
    categories = Category.query.all()
    for i in categories:
        shuffle(i.meals)
            
    return render_template("main.html", categories=categories, cart = get_cart(),
        user_id = get_id())

@app.route("/addtocart/<id>")
def add_cart(id):
    if not session.get("cart"):
        session["cart"] = dict()
    else:
        session["cart"] = json.loads(session["cart"])
    session["cart"][id] = session["cart"].get(id, 0) + 1
    session["cart"] = json.dumps(session["cart"])
    return redirect(url_for("cart"))

@app.route("/cart/", methods = ["GET", "POST"])
def cart():
    is_deleted = False
    if request.method == "POST":
        if request.form.get("DELETED"):
            is_deleted = True
            session["cart"] = json.loads(sessio["cart"])
            sessio["cart"].pop(request.form["DELETED"].split(" ")[1])
            session["cart"] = json.dumps(session["cart"])
            
    tmp = inside_cart()
    meals = dict()
    total_list = []
    
    if not tmp:
        cart2 = "Корзина пуста"
        tmp = ("","")
    else:
        meals = json.loads(session["cart"])
        cart2 = "{} блюда в корзине".format(tmp[0])
        for i in meals.items():
            meal = Meal.query.filter(Meal.id == int(i[0])).first()
            total_list.append((meal.title, i[1], meal.price * i[1], meal.id))
        
    mail = ""
    if session.get("user_id"):
        data = User.query.filter(User.id == int(session["user_id"])).first()
        mail = data.mail
        
    
    return render_template("cart.html", cart = get_cart(), cart2 = cart2,
            total_list = total_list, total_price = tmp[1], is_deleted = is_deleted,
            mail = mail, user_id = get_id())

@app.route("/account/")
def account():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    orders = Order.query.filter(Order.user_id == int(session["user_id"])).all()
    orders_with_value = dict()
    for order in orders:
        orders_with_value[order.id] = json.loads(order.json_order) 
    return render_template("account.html", cart = get_cart(), user_id = get_id(),
        orders = orders, orders_with_value = orders_with_value)

@app.route("/login/", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter(User.mail == request.form["mail"]).first()
        if not user:
            return render_template("login.html", trouble = "Неправильная почта")
        if not check_password_hash(user.password, request.form["password"]):
            return render_template("login.html", trouble = "Неправильный пароль")
        session["user_id"] = str(user.id)
        return redirect(url_for("first"))
    return render_template("login.html")

@app.route("/register/", methods = ["GET", "POST"])
def rergister():
    if request.method == "POST":
        if User.query.filter(User.mail == request.form["mail"]).first():
            return render_template("register.html", not_unique = True)
        user = User(mail = request.form["mail"],
            password = generate_password_hash(request.form["password"]))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = str(User.query.filter(User.mail == request.form["mail"]).first().id)
        return redirect(url_for("first"))
    
    return render_template("register.html")

@app.route("/logout/")
def logout():
    session.pop("user_id")
    return redirect(url_for("first"))

@app.route("/ordered/", methods = ["GET", "POST"])
def ordered():
    if request.method == "POST":
        total = 0
        tmp = json.loads(session["cart"])
        tmp_list = []
        
        order = Order(date = date.today(), status="ordered",
        mail=request.form["mail"], phone=request.form["phone"], address=request.form["address"],
        json_order=session["cart"], user_id=int(session["user_id"]))
        db.session.add(order)
        
        for i in tmp.items(): 
            meal = db.session.query(Meal).filter(Meal.id == int(i[0])).first()
            total += meal.price * int(i[1])
            order.meals.append(meal)
            
        order.summa = total
        db.session.commit()
        session.pop("cart")
        return render_template("ordered.html")
    else:
        return redirect(url_for("cart"))
            
if __name__ == "__main__":
	app.run(debug=False)