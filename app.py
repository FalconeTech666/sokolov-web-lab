from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests
import re

from translations import texts

app = Flask(__name__)
app.secret_key = 'super_secret_key_sokolov_2026'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Хеширует пароль и сохраняет в поле password_hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет, соответствует ли введённый пароль сохранённому хешу"""
        return check_password_hash(self.password_hash, password)

with app.app_context():
    db.create_all()

@app.route('/set-lang/<lang_code>')
def set_lang(lang_code):
    if lang_code in ['ru', 'en']:
        session['lang'] = lang_code
    return redirect(request.referrer or url_for('index'))

@app.context_processor
def inject_text():
    current_lang = session.get('lang', 'ru')
    return dict(t=texts[current_lang], current_lang=current_lang)

def get_current_user():
    """Возвращает объект User из БД, если пользователь залогинен"""
    login = session.get('user_login')
    if login:
        return User.query.filter_by(login=login).first()
    return None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped

@app.route('/')
def index():
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        age = request.form.get('age', '').strip()
        email = request.form.get('email', '').strip()
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()

        errors = []

        if not re.match(r'^[a-zA-Z0-9_]{6,20}$', login):
            errors.append("Логин: 6-20 символов, латиница, цифры, _")
        if not re.match(r'^[a-zA-Z0-9]{8,15}$', password):
            errors.append("Пароль: 8-15 символов, A-Z, a-z, 0-9")
        if not age.isdigit() or not (1 <= int(age) <= 120):
            errors.append("Возраст должен быть числом от 1 до 120")
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append("Введите корректный email")

        if User.query.filter_by(login=login).first():
            errors.append("Логин уже занят")
        if User.query.filter_by(email=email).first():
            errors.append("Email уже зарегистрирован")

        if errors:
            return render_template('register.html', user=user, errors=errors, form_data=request.form)

        new_user = User(
            login=login,
            email=email,
            first_name=first_name,
            last_name=last_name,
            age=int(age)
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        session['user_login'] = login
        return redirect(url_for('index'))

    return render_template('register.html', user=user)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    
    if request.method == 'POST':
        login_input = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()

        user_obj = User.query.filter_by(login=login_input).first()

        if user_obj and user_obj.check_password(password):
            session['user_login'] = user_obj.login
            return redirect(url_for('index'))
        else:
            return render_template('login.html', user=user, errors=['Неверный логин или пароль'])

    return render_template('login.html', user=user)

@app.route('/logout/')
def logout():
    session.pop('user_login', None)
    return redirect(url_for('index'))

@app.route('/duck/')
@login_required
def duck():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    response = requests.get('https://random-d.uk/api/random')
    data = response.json()
    
    return render_template('duck.html', user=user, image_url=data['url'], duck_number=data.get('message', 'N/A'))

@app.route('/fox/')
@app.route('/fox/<int:count>')
@login_required
def fox(count=1):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    images = []
    for _ in range(min(count, 10)):  
        res = requests.get('https://randomfox.ca/floof/')
        images.append(res.json()['image'])
    
    return render_template('fox.html', user=user, images=images, count=count)

def get_weather_for_city(city):
    api_key = 'c20b707c789771eddf22032f24f790ac' 
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            return None, f"Город '{city}' не найден"
        
        context = {
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'pressure': data['main']['pressure'],
            'icon_url': f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            'updated_at': datetime.now().strftime('%H:%M:%S')
        }
        return context, None
    except Exception as e:
        return None, str(e)

@app.route('/weather/', methods=['GET', 'POST'])
@login_required
def weather():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    city = "Minsk"
    if request.method == 'POST':
        city = request.form.get('city')

    context, error = get_weather_for_city(city)

    if error:
        return render_template('weather.html', user=user, error_message=error, city_display=city, temp=None)

    return render_template('weather.html', user=user, city_display=city, **context)

def get_nbrb_rates(date=None):
    if date is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    else:
        date_str = date

    url = f"https://api.nbrb.by/exrates/rates?ondate={date_str}&periodicity=0"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        target_currencies = ['USD', 'EUR', 'RUB']
        rates = {}
        
        for item in data:
            if item['Cur_Abbreviation'] in target_currencies:
                rates[item['Cur_Abbreviation']] = {
                    'rate': item['Cur_OfficialRate'],
                    'scale': item['Cur_Scale'],
                    'name': item['Cur_Name']
                }
        return rates, date_str
    except Exception as e:
        print(f"Error fetching NBRB rates: {e}")
        return None, date_str

@app.route('/rates/', methods=['GET', 'POST'])
@login_required
def rates():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    selected_date = datetime.now().strftime('%Y-%m-%d')
    conversion_result = None
    
    if request.method == 'POST':
        if 'date_picker' in request.form:
            selected_date = request.form.get('date_picker')
        
        if 'amount' in request.form:
            try:
                amount = float(request.form.get('amount'))
                currency_from = request.form.get('currency_from')
                currency_to = request.form.get('currency_to')
                calc_date = request.form.get('calc_date') or selected_date
                
                rates_data, _ = get_nbrb_rates(calc_date)
                
                if rates_data:
                    val_in_byn = 0
                    if currency_from == 'BYN':
                        val_in_byn = amount
                    elif currency_from in rates_data:
                        r = rates_data[currency_from]
                        val_in_byn = amount * r['rate'] / r['scale']
                    
                    final_res = 0
                    if currency_to == 'BYN':
                        final_res = val_in_byn
                    elif currency_to in rates_data:
                        r = rates_data[currency_to]
                        final_res = val_in_byn / (r['rate'] / r['scale'])
                    
                    conversion_result = {
                        'amount': amount,
                        'from': currency_from,
                        'to': currency_to,
                        'result': round(final_res, 4),
                        'date': calc_date
                    }
                    selected_date = calc_date
            except ValueError:
                pass

    rates_list, current_date_str = get_nbrb_rates(selected_date)

    return render_template('rates.html', user=user, rates=rates_list, selected_date=current_date_str, conversion=conversion_result)

@app.route('/homework/')
@login_required
def homework():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('homework.html', user=user)

@app.errorhandler(404)
def page_not_found(e):
    user = get_current_user()
    return render_template('404.html', user=user), 404

if __name__ == '__main__':
    app.run(debug=True)
