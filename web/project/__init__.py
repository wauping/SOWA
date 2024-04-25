import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask import Flask, session, jsonify, send_from_directory, redirect, url_for, request, render_template, make_response
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # def __init__(self, email):
    #     self.email = email
    def json(self):
        return {'id': self.id, 'username': self.username, 'email': self.email, 'password': self.password}


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image = db.Column(db.LargeBinary, nullable=True)  # null = FALSE in prod
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    location = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, id):
        return {'Alert': self.id}


with app.app_context():
    db.create_all()


@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)


@app.route("/")
def home():
    # Проверяем, аутентифицирован ли пользователь
    if "user_id" not in session:
        return redirect(url_for("login"))  # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
    user_id = session["user_id"]
    # Получаем алерты пользователя из базы данных
    alerts = Alert.query.filter_by(user_id=user_id).all()
    return render_template("home.html", alerts=alerts)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["username"] = user.username
            return redirect(url_for("home"))
        else:
            error = "Неверные учетные данные. Пожалуйста, попробуйте еще раз."
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists"
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return "User registered successfully"
    return render_template("login.html")


@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        new_user = User(username=data['username'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message': 'user created'}), 201)
    except Exception:
        return make_response(jsonify({'message': 'error creating user'}), 500)


@app.route('/alerts', methods=['POST'])
def create_alert():
    try:
        data = request.get_json()
        new_alert = Alert(image=data['image'], user_id=data['user_id'], location=data['location'], date_created=datetime.now)
        db.session.add(new_alert)
        db.session.commit()
        return make_response(jsonify({'message': 'alert created'}), 201)
    except Exception:
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


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """
