from flask import Flask, render_template, redirect, url_for, flash
from flask import request
from flask_admin import Admin, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///base.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secretkey"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
admin = Admin(app, template_mode='bootstrap4', name='Points', url='/rating')


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    group = db.Column(db.String(50), nullable=True)
    ktp = db.Column(db.Float, nullable=True)
    math = db.Column(db.Integer, nullable=True)
    physics = db.Column(db.Integer, nullable=True)
    web_technology = db.Column(db.Integer, nullable=True)
    okit = db.Column(db.Integer, nullable=True)
    kursova = db.Column(db.Integer, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    total = db.Column(db.Float, nullable=True)

    # on change
    def on_change(self):
        self.total = self.total_points()

    def total_points(self):
        sum = 0
        credit_ktp = credits.query.filter_by(name='КТП').first()
        credit_math = credits.query.filter_by(name='Вища математика').first()
        credit_physics = credits.query.filter_by(name='Фізика').first()
        credit_web_technology = credits.query.filter_by(name='Веб технології').first()
        credit_okit = credits.query.filter_by(name='ОКІТ').first()
        credit_kursova = credits.query.filter_by(name='Курсова').first()
        credit_sum = 0
        if self.ktp is not None and self.ktp >= 5:
            credit_sum += credit_ktp.credits
            sum += self.ktp * credit_ktp.credits
        if self.math is not None and self.math >= 5:
            credit_sum += credit_math.credits
            sum += self.math * credit_math.credits
        if self.physics is not None and self.physics >= 5:
            credit_sum += credit_physics.credits
            sum += self.physics * credit_physics.credits
        if self.web_technology is not None and self.web_technology >= 5:
            credit_sum += credit_web_technology.credits
            sum += self.web_technology * credit_web_technology.credits
        if self.okit is not None and self.okit >= 5:
            credit_sum += credit_okit.credits
            sum += self.okit * credit_okit.credits
        if self.kursova is not None and self.kursova >= 5:
            credit_sum += credit_kursova.credits
            sum += self.kursova * credit_kursova.credits
        if credit_sum == 0:
            return 0
        return sum / credit_sum

    def is_active(self):
        # Customize the logic to determine if the user is active or not
        # For example, you could check if the user's email is confirmed or any other condition
        return self.is_admin

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return f"Student('{self.name}', '{self.username}', '{self.group_name()}', '{self.ktp}', '{self.math}', '{self.physics}', '{self.web_technology}', '{self.okit}', '{self.kursova}')"


@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))


class credits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    credits = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        return f"Credits('{self.name}', '{self.credits}')"


class admin_base_view(ModelView):
    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class students_base_view(ModelView):
    def is_accessible(self):
        return current_user.is_anonymous or not current_user.is_admin

    can_create = False
    can_edit = False
    can_delete = False


class student_view(admin_base_view):
    column_list = (
        'rating',
        'name',
        'group',
        'ktp',
        'math',
        'physics',
        'web_technology',
        'okit',
        'kursova',
        'total'
    )

    # define name of column
    column_labels = dict(
        rating='Рейтинг',
        name='Name',
        ktp='КТП',
        math='Вишмат',
        physics='Фізика',
        web_technology='Веб',
        okit='ОКІТ',
        kursova='Курсова',
        group='Група',
    )

    def rating(view, context, model, name):
        # get rating
        students = Student.query.all()
        students.sort(key=lambda x: x.total_points(), reverse=True)
        for i in range(len(students)):
            if students[i].id == model.id:
                return i + 1
        return 0

    column_default_sort = ('total', True)

    column_formatters = {
        'rating': rating
    }


class credits_view(admin_base_view):
    column_list = ('name', 'credits')
    column_labels = dict(name='Назва',
                         credits='Кількість кредитів')


class recalculate(BaseView):
    @expose('/')
    def index(self):
        students = Student.query.all()
        for student in students:
            student.on_change()
            db.session.commit()
        return redirect(url_for('admin.index'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class student_view_st(students_base_view):
    column_list = (
        'rating',
        'name',
        'group',
        'ktp',
        'math',
        'physics',
        'web_technology',
        'okit',
        'kursova',
        'total'
    )

    # define name of column
    column_labels = dict(
        rating='Рейтинг',
        name='Name',
        ktp='КТП',
        math='Вишмат',
        physics='Фізика',
        web_technology='Веб',
        okit='ОКІТ',
        kursova='Курсова',
        group='Група',
    )

    def rating(view, context, model, name):
        # get rating
        students = Student.query.all()
        students.sort(key=lambda x: x.total_points(), reverse=True)
        for i in range(len(students)):
            if students[i].id == model.id:
                return i + 1
        return 0

    column_default_sort = ('total', True)

    column_formatters = {
        'rating': rating
    }


class credits_view_st(students_base_view):
    column_list = ('name', 'credits')
    column_labels = dict(name='Назва',
                         credits='Кількість кредитів')


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect(url_for('index'))

    def is_accessible(self):
        return current_user.is_authenticated



admin.add_view(student_view(Student, db.session))
admin.add_view(credits_view(credits, db.session))
admin.add_view(student_view_st(Student, db.session, endpoint='student_ro'))
admin.add_view(credits_view_st(credits, db.session, endpoint='credits_ro'))
admin.add_view(recalculate(name='Перерахувати', endpoint='recalculate'))
admin.add_view(LogoutView(name='Вийти', endpoint='logout'))



@app.route('/fill_credits')
def fill_credits():
    ktp = credits(name='КТП', credits=6)
    math = credits(name='Вища математика', credits=6)
    physics = credits(name='Фізика', credits=6)
    web_technology = credits(name='Веб технології', credits=5)
    okit = credits(name='ОКІТ', credits=3)
    kursova = credits(name='Курсова', credits=1.5)
    db.session.add(ktp)
    db.session.add(math)
    db.session.add(physics)
    db.session.add(web_technology)
    db.session.add(okit)
    db.session.add(kursova)
    db.session.commit()
    return redirect(url_for('admin.index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = Student.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Неправильний пароль', 'error')
        else:
            flash('Неправильний логін', 'error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    group = request.form.get("group")
    group = "1АКІТ-22б" if group == '1' else "2АКІТ-22б"
    student = Student.query.filter_by(username=username).first()
    if student:
        flash('Користувач з таким логіном вже існує', 'error')
        return render_template('register.html')

    if request.method == 'POST':
        student = Student(name=name, username=username, password=password, group=group)
        db.session.add(student)
        db.session.commit()
        login_user(student)
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        ktp = request.form.get("ktp")
        math = request.form.get("math")
        physics = request.form.get("physics")
        web_technology = request.form.get("web_technology")
        okit = request.form.get("okit")
        kursova = request.form.get("kursova")
        if ktp:
            current_user.ktp = float(ktp)
        if math:
            current_user.math = float(math)
        if physics:
            current_user.physics = float(physics)
        if web_technology:
            current_user.web_technology = float(web_technology)
        if okit:
            current_user.okit = float(okit)
        if kursova:
            current_user.kursova = float(kursova)
        current_user.on_change()
        db.session.commit()
    return render_template(
        'index.html',
        username=current_user.name,
        position=1,
        ktp=current_user.ktp,
        math=current_user.math,
        physics=current_user.physics,
        web_technology=current_user.web_technology,
        okit=current_user.okit,
        kursova=current_user.kursova,
    )


@app.route('/set_admin')
def set_admin():
    admin = Student.query.filter_by(username='joly54').first()
    admin.is_admin = True
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
