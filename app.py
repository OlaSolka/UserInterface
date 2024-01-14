from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sxdfcgvhb23355y4fwekdmcjbw///'  # unikatowy klucz
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login', username=email))

    return render_template('register.html')

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(email=username).first()

    if request.method == 'POST':
        # Aktualizacja danych profilu
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        db.session.commit()

    return render_template('profile.html', user=user)


# Funkcja sprawdzająca, czy użytkownik jest zalogowany
def is_logged_in():
    return 'user_id' in session

# Endpoint do logowania
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            login_user(user)
            return redirect(url_for('profile', username=user.email))
        else:
            flash('Invalid login credentials', 'danger')

    return render_template('login.html')


# Endpoint do wylogowywania
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.pop('user_id', None)
        flash('You have been logged out', 'success')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


