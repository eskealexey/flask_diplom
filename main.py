import os
from fileinput import filename
from os import path

from flask import Flask, render_template, request, redirect, url_for, flash, make_response

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import send_from_directory
from werkzeug.utils import secure_filename
from forms import RegisterForm, LoginForm, CreateTransistor
from models.models import Base, UserOrm, TransistorOrm, TypeOrm, KorpusOrm

# # конфигурация
DATABASE = '/tmp/database.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
USERNAME = 'admin'
PASSWORD = 'default'
# папка для сохранения загруженных файлов
# UPLOAD_FOLDER = '/path/to/the/uploads'

# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

UPLOAD_FOLDER = 'uploads'
UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# UPLOAD_FOLDER = os.path.join(app.root_path,'media/')
# Загружаем конфиг по умолчанию и переопределяем в конфигурации часть
# значений через переменную окружения
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'database.db'),
    DEBUG=True,
    SECRET_KEY='fdgfh78@#5?>gfhf89dx,v06k',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Подключаемся и создаем сессию базы данных
engine = create_engine('sqlite:///database.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/static/&lt;path:path&gt;')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/media/&lt;path:path&gt;')
def send_media(path):
    return send_from_directory('media', path)


# ===========Главная страница=================
@app.route('/')
@app.route('/home')
def home():
    return render_template('main.html')


# ========= переход на страницу Регистрации
@app.route('/registr', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = request.form['username']
        hash = generate_password_hash(request.form['pass1'])
        User = session.query(UserOrm).filter_by(username=username).first()
        if not User:
            newUser = UserOrm(username=username, password=hash, status=0)
            session.add(newUser)
            # session.flush()
            session.commit()
            return render_template('registration_ok.html', user=username)

    return render_template("registration.html", title="Регистрация", form=form)


# ============== авторизация пользователя ===========
@app.route('/login', methods=['GET', 'POST'])
def log_in():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['username']
        password = request.form['password']
        user = session.query(UserOrm).filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                id = str(user.id)
                res = make_response(redirect('/home'))
                res.set_cookie('userid', id, max_age=None)
                res.set_cookie('username', user.username, max_age=None)
                return res
                return render_template("main.html", title="Главная", )
            else:
                print('пароль неверный')
        else:
            print('нет пользователя')

    return render_template("login.html", title="Авторизация", form=form)


# ===================показ транзисторов===================
@app.route('/transistors')
def view_transistors():
    userid = request.cookies.get('userid')
    data = session.query(TransistorOrm).filter_by(userid=userid).all()

    return render_template('transistor.html', transistors=data)


# ==================создать транзистор====================
@app.route('/create', methods=['GET', 'POST'])
def create_transistor():
    types = session.query(TypeOrm).all()
    korpus = session.query(KorpusOrm).all()
    if request.method == 'POST':
        name = request.form.get('name')
        markname = request.form.get('markname')
        type_ = request.form.get('type_')
        korpus = request.form.get('korpus')
        descr = request.form.get('descr')
        user_id = request.form.get('user_id')

        newTransistor = TransistorOrm(
            name=name,
            markname=markname,
            type_=type_,
            korpus=korpus,
            descr=descr,
            userid=user_id
        )
        session.add(newTransistor)
        session.flush()
        id = newTransistor.id
        session.commit()
        return redirect(url_for('transistor', id=id))
        # return render_template('transistor_forma_add.html')
    return render_template('transistor_forma_add.html', types=types, korpus=korpus, title="Новый")


# ==========================вывод одного транзистора=========================
@app.route('/transistor/<id>', methods=['GET', 'POST'])
def transistor(id):
    data = session.query(TransistorOrm).where(TransistorOrm.id == id).one()
    types = session.query(TypeOrm.type_name).where(TypeOrm.id == data.type_).one()
    korpus = session.query(KorpusOrm.korpus_name).where(KorpusOrm.id == data.korpus).one()

    return render_template('transistor_id.html', transistor=data, types=types, korpus=korpus)


# ==============================добавление / удаление========================================
@app.route('/amount/', methods=['GET', 'POST'])
def amount():
    id = request.form.get('trid')
    trans = session.query(TransistorOrm).where(TransistorOrm.id == id).first()
    total = int(trans.amount)
    act = request.form.get('act')
    quantity = request.form.get('quantity')
    if act is not None:
        if act == 'add':
            total += int(quantity)
        elif (act == 'del') and (total >= int(quantity)):
            total -= int(quantity)
        else:
            error = 'удаляется больше чем есть'
    trans.amount = total

    session.commit()

    userid = request.cookies.get('userid')
    data = session.query(TransistorOrm).filter_by(userid=userid).all()

    return render_template('transistor.html', transistors=data)


# ============================загрузка файла даташит на сервер
def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # проверим, передается ли в запросе файл
        if 'path_file' not in request.files:
            # После перенаправления на страницу загрузки
            # покажем сообщение пользователю
            flash('Не могу прочитать файл')
            return redirect(request.url)
        file = request.files['path_file']
        # Если файл не выбран, то браузер может
        # отправить пустой файл без имени.
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # безопасно извлекаем оригинальное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            id = request.form.get('trid')
            trans = session.query(TransistorOrm).where(TransistorOrm.id == id).first()
            trans.path_file = f'{filename}'
            session.commit()

            return redirect(url_for('view_transistors', name=filename))
    return


# ===============================редактирование транзистора===================================
@app.route('/transistor/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    transistor = session.query(TransistorOrm).where(TransistorOrm.id == id).one()
    types = session.query(TypeOrm).all()
    korpus = session.query(KorpusOrm).all()

    if request.method == 'POST':
        transistor.name = request.form.get('name')
        transistor.markname = request.form.get('markname')
        transistor.type_ = request.form.get('type_')
        transistor.korpus = request.form.get('korpus')
        transistor.descr = request.form.get('descr')
        session.commit()
        return redirect(url_for('transistor', id=transistor.id))
    return render_template(
        'transistor_edit.html',
        transistor=transistor,
        types=types,
        korpus=korpus
    )

#================поиск в наименовании==========================
@app.route('/find', methods=['GET', 'POST'])
def find():
    userid = request.cookies.get('userid')
    if request.method == 'POST':
        str_ = request.form.get('find')
        # transistors = session.query(TransistorOrm).filter(TransistorOrm.name == str_).all()

        transistors = session.query(TransistorOrm).filter(TransistorOrm.name.like(f'%{str_}%'), TransistorOrm.userid == userid).all()
        print(transistors)
    return render_template('transistor.html', transistors=transistors)

#================================log_out================================
@app.route('/logout', methods=['GET','POST'])
def logout():
    resp = make_response(render_template('main.html'))
    resp.delete_cookie('userid')
    resp.delete_cookie('username')
    # resp.del_cookie()
    # resp.del_cookie('username')
    # возвращаем измененный ответ
    return resp



if __name__ == '__main__':
    app.run()
