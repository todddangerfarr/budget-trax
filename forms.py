from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from models import Merchant, Category

class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class ExpenseForm(Form):
    date = DateField('DatePicker', format='%Y-%m-%d')
    merchant = QuerySelectField(
        query_factory=lambda: Merchant.query.order_by(Merchant.name).all())
    category = QuerySelectField(
        query_factory=lambda: Category.query.order_by(
        Category.category_text).all())
    description = StringField('Description')
    cost = StringField('Expense Amount', validators=[DataRequired()])


class CategoryForm(Form):
    category = StringField('Category', validators=[DataRequired()])


class MerchantForm(Form):
    merchant = StringField('Merchant', validators=[DataRequired()])
