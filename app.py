from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user, logout_user, login_user
import os
import smtplib
from email.mime.text import MIMEText
from random import randint

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = 'hardsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbase.db'
# app.config['STATIC'] = 'static'
db = SQLAlchemy(app)

IMAGES_FOLDER = os.path.join('static', 'img')
app.config['UPLOAD_FOLDER'] = IMAGES_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    surname1 = db.Column(db.String(100))
    name = db.Column(db.String(100))
    role = db.Column(db.Integer())
    image = db.Column(db.String(500))


# таблица с курсами
class Training_course(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # id курса
    mentor = db.Column(db.Integer())  # id настаника (создателя курса)
    name = db.Column(db.String(100), unique=True)  # название курса
    description = db.Column(db.String(1000), unique=True)  # описание курса
    kol_lessons = db.Column(db.Integer())  # кол-во уроков
    names_lessons = db.Column(db.String(50000))  # названия уроков
    kol_positive = db.Column(db.Integer())  # кол-во позитивных оценок
    kol_negative = db.Column(db.Integer())  # кол-во негативных оценок


# таблица с уроками
class Training_lesson(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)  # id урока
    mentor = db.Column(db.Integer())  # id настаника (создателя курса)
    id_course = db.Column(db.Integer())  # id курса
    num_lesson = db.Column(db.Integer())  # номер урока в курсе
    name = db.Column(db.String(100), unique=True)  # название курса
    theory = db.Column(db.String(10000), unique=True)  # теоретическая часть
    video = db.Column(db.String(200), unique=True)  # видео часть
    test = db.Column(db.String(10000), unique=True)  # тестирующая часть
    practice = db.Column(db.String(10000), unique=True)  # задачи для решения


with app.app_context():
    db.create_all()

LESSONS = []
KOL = 0


@app.route('/course', methods=['GET', 'POST'])
@login_required
def course():
    c = Training_course.query.filter_by(mentor=current_user.id).first()

    name = c.name
    description = c.description

    kol_lessons = c.kol_lessons
    names_lessons = c.names_lessons.split(";")
    kol_positive = c.kol_positive
    kol_negative = c.kol_negative
    les = []
    return render_template('kurs.html', mentor=current_user.name, name=name, description=description,
                           kol_lessons=kol_lessons,
                           names_lessons=names_lessons, kol_positive=kol_positive, kol_negative=kol_negative)


@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    global KOL, LESSONS
    if request.method == 'POST':
        name = request.form['name_course']
        desc = request.form['desc_course']
        if 'save' in tuple(request.form):
            print(LESSONS, KOL, request.form['name_course'], )

            # mentor = db.Column(db.Integer())  # id настаника (создателя курса)
            # name = db.Column(db.String(100), unique=True)  # название курса
            # description = db.Column(db.String(1000), unique=True)  # описание курса
            # kol_lessons = db.Column(db.Integer())  # кол-во уроков
            # names_lessons = db.Column(db.String(50000))  # названия уроков
            # kol_positive = db.Column(db.Integer())  # кол-во позитивных оценок
            # kol_negative = db.Column(db.Integer())  # кол-во негативных оценок

            new_course = Training_course(mentor=current_user.id, name=name, description=desc, kol_lessons=KOL,
                                         names_lessons=';'.join(LESSONS), kol_positive=0, kol_negative=0)

            db.session.add(new_course)
            db.session.commit()
            KOL = 0
            LESSONS = []
            return redirect(url_for('course'))
        if 'delete' in tuple(request.form):
            if KOL != 0:
                KOL -= 1
                del LESSONS[-1]
                return render_template('create_course.html', lessons=LESSONS, kol=KOL, desc=desc, name_course=name)
            else:
                return render_template('create_course.html', lessons=LESSONS, kol=KOL, desc=desc, name_course=name)
        if request.form['add'] == 'Добавить урок':
            KOL += 1
            LESSONS.append('')

        print(request.form)

        for i in range(KOL - 1):
            lsn = request.form['name_lesson ' + str(i)]
            print(lsn)
            LESSONS[i] = lsn
        print(KOL, LESSONS)
        name = request.form['name_course']
        desc = request.form['desc_course']
        return render_template('create_course.html', lessons=LESSONS, kol=KOL, desc=desc, name_course=name)
    else:
        return render_template('create_course.html', lessons=LESSONS, kol=KOL)


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        upd = request.form
        print(tuple(upd))
        flag = 1
        if 'update' in tuple(upd):
            return redirect(url_for('update'))
        if 'theory' in tuple(upd):
            flag = 1
        if 'video' in tuple(upd):
            flag = 2
        if 'test' in tuple(upd):
            flag = 3
        if 'practice' in tuple(upd):
            flag = 4
        return render_template('update.html', flag=flag)
    else:
        return render_template('update.html')


@app.route('/lesson', methods=['GET', 'POST'])
def lesson():
    if request.method == 'POST':
        teo = request.form
        print(tuple(teo))
        flag = 1
        if 'update' in tuple(teo):
            return redirect(url_for('update'))
        if 'theory' in tuple(teo):
            flag = 1
        if 'video' in tuple(teo):
            flag = 2
        if 'test' in tuple(teo):
            flag = 3
        if 'practice' in tuple(teo):
            flag = 4
        return render_template('lesson.html', flag=flag)
    else:
        return render_template('lesson.html', flag=1)


@app.route('/')
def index():
    if current_user.is_authenticated:
        flag_user = True
    else:
        flag_user = False

    return render_template('N_1.html', flag=flag_user)


def send_email(message, adress):
    sender = "gulovskiu@gmail.com"
    password = "nwjcfhzloyluetwv"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender, password)
        msg = MIMEText(message)
        msg["Subject"] = "Восстановление пароля"
        server.sendmail(sender, adress, msg.as_string())
        return "The message was sent successfully!"
    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/new_password', methods=['GET', 'POST'])
def new_password():
    if request.method == 'POST':
        psw1 = request.form['psw1']
        psw2 = request.form['psw2']
        if not psw1 or not psw2:
            return render_template('new_password.html', err='Заполните все поля', psw1=psw1, psw2=psw2)
        if len(psw1) < 8:
            return render_template('new_password.html', err='Пароль слишком маленький', psw1=psw1, psw2=psw2)
        if psw1 != psw2:
            return render_template('new_password.html', err='Пароли различаются', psw1=psw1, psw2=psw2)
        # добавить условие для сложностей паролей
        # return render_template('new_password.html', psw1='', psw2='')
        email = session.get('email', None)
        user = User.query.filter_by(email=email).first()
        if user != '':
            user.password = psw1
            db.session.commit()
        return redirect(url_for('login'))
    else:
        return render_template('new_password.html', psw1='', psw2='')


CODE = 0


@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        global CODE
        print(request.form)
        email = request.form['mail']
        unic_code = request.form['unik_cod']
        if email == '':
            return render_template('password.html', flag=False, err="Введите почту")
        if unic_code == '':
            flag = True
            CODE = randint(1000, 9999)
            message = (f'''Здравствуйте!
            Вы получили это письмо, потому что мы получили запрос на сброс пароля для вашей учетной записи.
            Специальный код для сброса пароля: {CODE}
            Если вы не запрашивали сброс пароля, никаких дальнейших действий не требуется.

            С Уважением,
            EdTech платформа''')
            print(send_email(message=message, adress=email))
            return render_template('password.html', flag=True, err="Код отправлен", email=email)
        else:
            if int(unic_code) == CODE:
                CODE = 0
                session['email'] = email
                return redirect(url_for('new_password'))
    else:
        return render_template('password.html', flag=False, err="")


@app.route('/profile')
@login_required
def profile():
    r = ""
    if current_user.role == 0:
        r = "Студент"
    elif current_user.role == 1:
        r = "Наставник"
    elif current_user.role == 2:
        r = "Администратор"

    return render_template('profile.html', name=current_user.name, surname=current_user.surname,
                           surname1=current_user.surname1, email=current_user.email, image='img/' + current_user.image,
                           role=r)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        print(request.form)
        if 'name' in tuple(request.form):
            name = request.form.get('name')
            cu = User.query.filter_by(id=current_user.id).first()
            cu.name = name
            db.session.commit()
        if 'surname' in tuple(request.form):
            surname = request.form.get('surname')
            cu = User.query.filter_by(id=current_user.id).first()
            cu.surname = surname
            db.session.commit()
        if 'surname1' in tuple(request.form):
            surname1 = request.form.get('surname1')
            cu = User.query.filter_by(id=current_user.id).first()
            cu.surname1 = surname1
            db.session.commit()
        if 'upload_image' in tuple(request.form):
            file = request.files['file']
            if file.filename != '':

                if file.filename.split(".")[-1].upper() not in "PNG, JPEG, GIF, RAW, TIFF, BMP, PSD":
                    return render_template('edit_profile.html', name=current_user.name, surname=current_user.surname,
                                           surname1=current_user.surname1, email=current_user.email,
                                           image='img/' + current_user.image, error="Ошибка расширения")
                cu = User.query.filter_by(id=current_user.id).first()
                cu.image = file.filename
                db.session.commit()
                # безопасно извлекаем оригинальное имя файла
                filename = file.filename
                # сохраняем файл
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('edit_profile.html', name=current_user.name, surname=current_user.surname,
                                   surname1=current_user.surname1, email=current_user.email,
                                   image='img/' + current_user.image)
        else:
            return redirect(url_for('profile'))
    else:

        return render_template('edit_profile.html', name=current_user.name, surname=current_user.surname,
                               surname1=current_user.surname1, email=current_user.email,
                               image='img/' + current_user.image)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('password')
        remember = request.form.get('rememder')
        if remember:
            remember = True
        else:
            remember = False
        print(email, password, remember)
        if not email or not password:
            return render_template('entrance.html', err='Заполнены не все поля')
        user = User.query.filter_by(email=email).first()
        if not user:
            return render_template('entrance.html', err='Почта не зарегистрирована')

        # user = User.query.filter((User.email == email) | (User.password == password)).first()
        #
        # if user.password != password:
        #     return render_template('entrance.html', err='Неверный пароль')
        user = User.query.filter((User.email == email) & (User.password == password)).first()

        if user:
            login_user(user, remember=remember)
            return redirect(url_for('index'))
        else:
            return render_template('entrance.html', err='Проверьте данные')
    else:
        return render_template('entrance.html', err='')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        surname = request.form.get('surname')
        surname1 = request.form.get('surname1')
        password = request.form.get('password')
        password1 = request.form.get('password1')
        role = 0
        image = 'profile-rev.png'
        if not email or not name or not surname or not surname1 or not password or not password1:
            return render_template('n_3.html', err="Заполнены не все поля")
        if '@' not in email:
            return render_template('n_3.html', err="Некорректная почта")
        if len(password) < 8:
            return render_template('n_3.html', err="Пароль слишком короткий")
        if password != password1:
            return render_template('n_3.html', err="Пароли не совпадают")
        user = User.query.filter_by(
            email=email).first()
        if user:
            return render_template('n_3.html', err="Пользователь с такой почтой уже зарегистрирован")
        new_user = User(email=email, name=name, surname=surname, surname1=surname1, password=password, role=int(role),
                        image=image)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('profile'))
    else:
        return render_template('n_3.html', err="")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
