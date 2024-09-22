from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo


class RegisterForm(FlaskForm):
    username = StringField("Имя пользователя: ", validators=[DataRequired()])
    pass1 = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=20)])
    pass2 = PasswordField("Повторите пароль:", validators=[DataRequired(), Length(min=4, max=20),
                           EqualTo('pass1', message="Пароли не совпадают")])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    username = StringField("Логин:", validators=[DataRequired()])
    password = PasswordField("Пароль:", validators=[DataRequired()])
    submit = SubmitField("Войти")

class CreateTransistor(FlaskForm):
    name = StringField("Наименование:", validators=[DataRequired()])
    markname = StringField("Маркировка", validators=[DataRequired()])
    type_ = SelectField("Тип:", validators=[DataRequired()])
    korpus = SelectField("Корпус:", validators=[DataRequired()])
    descr = TextAreaField("Краткое описание:")
    user_id = HiddenField('')
    submit = SelectField("Записать")

