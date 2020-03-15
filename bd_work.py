from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.orm import mapper, sessionmaker

engine = create_engine('sqlite:///databases/test_base.db', echo=True)
Session = sessionmaker(bind=engine)  # Фабрика сессий для бд

metadata = MetaData()  # Создаём базу и две таблицы, если их нет.
users_table = Table('users', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('login', String, unique=True),  # Каждого юзера создаём только один раз
                    Column('password', String),
                    Column('created_at', String)  # Дата создания записи
                    )

attempts_table = Table('attempts', metadata,
                       Column('id', Integer, primary_key=True, autoincrement=True),
                       Column('user_id', Integer, unique=True),  # Это id из первой таблицы!
                       Column('attempts_count', String),
                       Column('last_attempt', String)  # Дата последней попытки подключения
                       )

metadata.create_all(engine)


# Объявляем классы для работы с базой
class User(object):
    def __init__(self, id, login, password, created_at):
        self.id         = id
        self.login      = login
        self.password   = password
        self.created_at = created_at

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s')>" % (self.id, self.login, self.password, self.created_at)


class Attempt(object):
    def __init__(self, id, user_id, attempts_count, last_attempt):
        self.id             = id
        self.user_id        = user_id
        self.attempts_count = attempts_count
        self.last_attempt   = last_attempt

    def __repr__(self):
        return "<Attempt('%s', '%s', '%s', '%s')>" % (self.id, self.user_id, self.attempts_count, self.last_attempt)


# Привязываем классы к таблицам в базе
mapper(User, users_table)
mapper(Attempt, attempts_table)
