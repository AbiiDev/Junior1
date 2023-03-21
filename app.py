from flask import Flask, render_template, url_for, request, redirect, json
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    intro = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User %r' % self.id


class UserList(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

    def get(self):
        user = User.query.all()
        user_list = UserList(many=True)
        return user_list.dump(user)


@app.route('/api/main', methods=['GET'])
def get_user():
    user = User.query.all()
    user_list = UserList(many=True)
    return json.dumps(user_list.dump(user), ensure_ascii=False)


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/about')
def index():
    return render_template("about.html")


@app.route('/users')
def users():
    user = User.query.order_by(User.date.desc()).all()
    return render_template("users.html", user=user)


@app.route('/users/<int:id>')
def users_detail(id):
    user_detail = User.query.get(id)
    return render_template("users_detail.html", user_detail=user_detail)


@app.route('/users/<int:id>/delete')
def users_delete(id):
    user_info = User.query.get_or_404(id)

    try:
        db.session.delete(user_info)
        db.session.commit()
        return redirect('/users')
    except:
        return "При удалении пользователя произошла ошибка"


@app.route('/users/<int:id>/update', methods=['POST', 'GET'])
def users_update(id):
    user_update = User.query.get(id)
    if request.method == 'POST':
        user_update.title = request.form['title']
        user_update.intro = request.form['intro']
        user_update.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/users')
        except:
            return "При редактировании информации произошла ошибка"
    else:
        return render_template("users_update.html", user_update=user_update)


@app.route('/users-list', methods=['POST', 'GET'])
def users_list():
    if request.method == 'POST':
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        user = User(title=title, intro=intro, text=text)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/users')
        except:
            return "При добавлении информации произошла ошибка"
    else:
        return render_template("users-list.html")


if __name__ == '__main__':
    app.run(debug=True, port=5000, host="127.0.0.1")
