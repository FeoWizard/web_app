from flask import Flask, url_for, request, session
from flask import render_template
from werkzeug.utils import redirect

import datetime
import os

import bd_work

app = Flask(__name__)  # Создаём объект серверного приложения и передаём туда имя модуля


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
def index():  # "Главная" страница с формой логина

    if request.method == 'POST':

        # Получаем "голые" строки с формы
        username = request.form['login']
        password = request.form['pass']

        # Удаляем пробелы в конце и в начале строк
        # (Начинаться с пробела не пасс, не логин, энивей, не могут)
        username = username.strip(" ")
        password = password.strip(" ")

        if ((username != '') and (password != '')):  # Проверяем, что и логин, и пароль введены

            db_session = bd_work.Session(expire_on_commit = False)  # Локально создаём сессию для работы с базой

            # Читаем запись из базы с таким username, если возвращено 0 записей (None) -
            # то юзер новый, и тогда идём по основной ветке
            user = db_session.query(bd_work.User).filter_by(login = username).first()

            # Если возвращена 1 запись (username уникален, т.е. больше одной не вернётся в принципе),
            # то юзер уже есть и надо проверить количество попыток, а далее - проверить пароль.
            if (user):

                attempt = db_session.query(bd_work.Attempt).filter_by(user_id = user.id).first()

                if (int(attempt.attempts_count) >= 5):  # Если счётчик больше или равен 5, то больше не логиним юзера
                    return render_template('index.html', login_block = True)

                if (user.password == password):
                    # 'Пароль верен!'

                    # Если пароль верен - сбрасываем счётчик попыток. (Апдейтим запись)
                    db_session.query(bd_work.Attempt).filter_by(user_id = user.id).update(
                        {'attempts_count': 0, 'last_attempt': get_current_time()})
                    db_session.commit()
                    db_session.close()

                    session['user'] = user.login
                    return redirect(url_for('logged'))
                else:
                    # 'Неправильный пароль!'

                    # Если пароль неправильный - увеличиваем счётчик попыток. (Апдейтим запись)
                    db_session.query(bd_work.Attempt).filter_by(user_id = user.id).update(
                        {'attempts_count': int(attempt.attempts_count) + 1, 'last_attempt': get_current_time()})
                    db_session.commit()
                    db_session.close()

                    return render_template('index.html', invalid_password = True)

            else:

                user = bd_work.User(None, username, password, get_current_time())
                db_session.add(user)
                db_session.commit()

                # Объект сессии записывает в объект User значение id - то, которое было записано в базе.
                # Т.е. не нужно вручную считывать только что сделанную запись, чтобы узнать, какой же id у нового юзера

                attempt = bd_work.Attempt(None, user.id, 0, get_current_time())
                db_session.add(attempt)
                db_session.commit()

                db_session.close()  # Закрываем сессию работы с базой

                session['user'] = user.login  # Записываем в cookies

                return redirect(url_for('logged'))
        else:
            # Если логин или пароль являются пустой строкой, то просто "сбрасываем" форму.
            return render_template('index.html')
    else:
        # Если запрос не POST (не с формы), то просто отдаём страничку.
        return render_template('index.html')


@app.route('/logged', methods = ['GET', 'POST'])
def logged():

    try:  # Не даёт просто так лезть на страницу logged, только если есть соответствующие куки
        user = session['user']  # А здесь читаем из cookies, чтобы отобразить в шаблоне имя вошедшего пользователя
        user = user.strip('\"')
    except Exception:
        return redirect(url_for('index'))

    if request.method == 'POST':
        q = request.form  # "Магическая" строка, ничего не делает, но без обращения к request.form почему-то не работает
        session['user'] = None  # Удаляем куки при разлогине, чтобы перенаправляться на индекс
        return redirect(url_for('index'))
    else:
        return render_template('logged.html', username = user)


app.secret_key = os.urandom(24)  # Ключ для куки
app.run(debug = True)  # Запуск серверного приложения
