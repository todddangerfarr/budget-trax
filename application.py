from flask import (Flask, render_template, url_for, g, redirect, flash,
                   session, request)
from flask_login import (LoginManager, login_user, logout_user, current_user,
                         login_required)
from flask_bcrypt import Bcrypt
from forms import LoginForm, ExpenseForm, MerchantForm, CategoryForm, BudgetForm
from models import db, User, Merchant, Category, Expense, Budget
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
import datetime
import calendar

# application constants
DEBUG = True
PORT = 5000
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
            flash("Welcome {}, you've been logged in!".format(user.username),
                  "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Your username or password is incorrect!")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out", "info")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = g.user
    recent_expenses = Expense.query.order_by(
                      Expense.date.desc()).limit(10).all()
    budgets = Budget.query.all()
    return render_template('dashboard.html', user=user,
        recent_expenses = recent_expenses, budgets=budgets)

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

@app.route('/create_budget', methods=('GET', 'POST'))
@login_required
def add_budget():
    user = g.user
    form = BudgetForm()
    if form.validate_on_submit():
        budget = Budget(
            category = form.category.data,
            limit = ''.join(i for i in form.limit.data.strip() if i.isdigit())
        )
        db.session.add(budget)
        db.session.commit()
        flash("You've created a budget for: {}".format(
            form.category.data.category_text.title()), 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_budget.html', user=user, form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


############################################################# CONTEXT PROCESSORS
@app.context_processor
def utility_processor():
    def get_budget_total(budget, date):
        """ A context processor used to return the running total of the budget
        object expenses. """
        total = 0
        first_day_of_month = date.replace(day=1)
        last_day_of_month = date.replace(
                day=calendar.monthrange(date.year, date.month)[1]
            )
        expenses = budget.category.expenses.filter(
                Expense.date > first_day_of_month,
                Expense.date < last_day_of_month
            )
        if expenses != None:
            for expense in expenses:
                total += expense.cost
        return total

    def get_today():
        """ A context processor to return today's date. """
        return datetime.date.today()

    def get_days_in_month(year, month):
        """ A context processpr to return the days in the month. """
        return calendar.monthrange(year, month)[1]

    def get_marker_loc(today, days_in_month):
        """ A context processor to return the marker location for budgets. """
        return int((today / days_in_month) * 100)

    def get_recent_budget_history(num_months):
        """ A context processor to return the previous num_months of budget
            information for the dashboard. """
        today = get_today()
        budget_history_dict = OrderedDict()
        for i in range(1, num_months+1):
            calculated_date = today - relativedelta(months=i)
            key = (calendar.month_name[calculated_date.month], calculated_date.year)
            budget_history_dict[key] = {}
            for budget in Budget.query.all():
                budget_history_dict[key][budget.category.category_text] = get_budget_total(budget, calculated_date)

        return budget_history_dict


    return dict(get_budget_total=get_budget_total, get_today=get_today,
        get_days_in_month=get_days_in_month, get_marker_loc=get_marker_loc,
        get_recent_budget_history=get_recent_budget_history)


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
