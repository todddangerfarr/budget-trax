from flask import (Flask, render_template, url_for, g, redirect, flash,
                   session, request)
from flask_login import (LoginManager, login_user, logout_user, current_user,
                         login_required)
from flask_bcrypt import Bcrypt
from forms import LoginForm, ExpenseForm, MerchantForm, CategoryForm
from models import db, User, Merchant, Category, Expense

# application constants
DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

# create and setup the flask application object
app = Flask(__name__)
app.config.from_object('config')
bcrypt = Bcrypt(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    # g.db = models.DATABASE
    # g.db.connect()
    g.user = current_user


# @app.after_request
# def after_request(response):
#     """Close the database connection after each request."""
#     g.db.close()
#     return response


@app.route('/')
def index():
    user = g.user
    return render_template('index.html', user=user)

@app.route('/login', methods=('GET', 'POST'))
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if (user != None and bcrypt.check_password_hash(
                             user.password, form.password.data)):
            login_user(user)
            flash("You've been logged in!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Your username or password is incorrect!")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out!")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = g.user
    recent_expenses = Expense.query.limit(10).all()
    return render_template('dashboard.html', user=user,
        recent_expenses = recent_expenses)

@app.route('/add_expense', methods=('GET', 'POST'))
@login_required
def add_expense():
    user = g.user
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            date = form.date.data,
            description = form.description.data.strip(),
            cost = ''.join(
                i for i in form.cost.data.strip() if i.isdigit()),
            merchant = form.merchant.data,
            category = form.category.data,
            creator = user 
        )
        db.session.add(expense)
        db.session.commit()
        flash("The Expense from: '{}' was added".format(
            form.merchant.data.name), 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html', user=user, form=form)

@app.route('/add_category', methods=('GET', 'POST'))
@login_required
def add_category():
    user = g.user
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            category = db.session.query(Category).filter_by(
                category_text = form.category.data.strip().lower()).one()
        except:
            category = Category(
                category_text=form.category.data.strip().lower())
            db.session.add(category)
            db.session.commit()
            flash("The Category: '{}' was added".format(
                form.category.data.strip()), 'success')
            return redirect(url_for('dashboard'))
    return render_template('add_category.html', user=user, form=form)

@app.route('/add_merchant', methods=('GET', 'POST'))
@login_required
def add_merchant():
    user = g.user
    form = MerchantForm()
    if form.validate_on_submit():
        try:
            merchant = db.session.query(Merchant).filter_by(
                name = form.merchant.data.strip().lower()).one()
        except:
            merchant = Merchant(name=form.merchant.data.strip().lower())
            db.session.add(merchant)
            db.session.commit()
            flash("The Merchant: '{}' was added".format(
                form.merchant.data.strip()), 'success')
            return redirect(url_for('dashboard'))
    return render_template('add_merchant.html', user=user, form=form)

# start flask application
if __name__ == '__main__':
    with app.app_context():
        try:
            todd = db.session.query(User).filter_by(
                username='todddangerfarr').one()
        except:
            admin = User(username='todddangerfarr',
                email='todd.farr@gmail.com',
                password = bcrypt.generate_password_hash('password')
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=DEBUG, host=HOST, port=PORT)
