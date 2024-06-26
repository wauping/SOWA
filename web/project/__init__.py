from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from flask import Flask, session, jsonify, flash, send_from_directory, redirect, url_for, request, render_template, make_response


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def json(self):
        return {'id': self.id,
                'login': self.login,
                'username': self.username,
                'email': self.email,
                'password': self.password}


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.String(100))
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    location = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def json(self):
        return {'id': self.id,
                'user_id': self.user_id,
                'location': self.location,
                'date_created': self.date_created,
                'image': self.image}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    if "user_id" not in session:
        error = "Для просмотра оповещений необходима авторизация"
        flash(error)
        return redirect(url_for("login"))
    user_id = session["user_id"]
    alerts = Alert.query.filter_by(user_id=user_id).all()
    return render_template("home.html", alerts=alerts)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        data = request.form
        login = data.get("login")
        password = data.get("password")
        user = User.query.filter_by(login=login, password=password).first()
        if user:
            session["login"] = user.login
            session["username"] = user.username
            session["user_id"] = user.id
            return redirect(url_for("home"))
        else:
            error = "Неверные учетные данные. Пожалуйста, попробуйте еще раз."
            flash(error)
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        login = data.get("login")
        email = data.get("email")
        password = data.get("password")

        if not (username and email and password and login):
            error = "Необходимо заполнить все поля"
            return render_template("register.html", error=error)

        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            error = "Такой логин уже существует"
            return render_template("register.html", error=error)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = "Некорректный почтовый адрес"
            return render_template("register.html", error=error)

        new_user = User(login=login, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        success = "Пользователь зарегистрирован!"
        return render_template("login.html", success=success)
    return render_template("register.html")


@app.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        session.pop('login', None)
    return redirect(url_for('login'))


@app.route('/alerts', methods=['POST'])
def create_alert():
    try:
        data = request.form
        user_id = data.get('user_id')
        location = data.get('location')
        image = data.get('image')
        print(image)

        if user_id is None or location is None:
            return make_response(jsonify({'message': 'user_id and location are required fields'}), 400)

        new_alert = Alert(user_id=user_id, location=location, image=image)
        db.session.add(new_alert)
        db.session.commit()

        return make_response(jsonify({'message': 'alert created'}), 201)
    except Exception as e:
        print(e)
        return make_response(jsonify({'message': 'error creating alert'}), 500)


@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({'message': 'user not found'}), 404)
    except Exception:
        return make_response(jsonify({'message': 'error deleting user'}), 500)


@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(jsonify([user.json() for user in users]), 200)
    except Exception:
        return make_response(jsonify({'message': 'error getting users'}), 500)


@app.route('/alerts', methods=['GET'])
def get_alerts():
    try:
        alerts = Alert.query.all()
        return make_response(jsonify([alert.json() for alert in alerts]), 200)
    except Exception:
        return make_response(jsonify({'message': 'error getting alerts'}), 500)


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)
