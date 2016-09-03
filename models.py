from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(100))
    expenses = db.relationship('Expense', backref='creator', lazy='dynamic')

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3

    def __repr__(self):
        return '<User {}>'.format(self.username) # how this class is displayed


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    description = db.Column(db.String(160))
    cost = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Purchase {}>'.format(self.description)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_text = db.Column(db.String(120), unique=True)
    expesnes = db.relationship('Expense', backref='category', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.category_text.title())


class Merchant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    expenses = db.relationship('Expense', backref='merchant', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name.title())
