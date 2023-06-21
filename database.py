import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session
import psycopg2

from settings import password, dsn

Base = declarative_base()

class Viewed(Base):
    """Создание отношения для хранения данных о просмотрах"""
    __tablename__ = 'viewed'
    sender_id = sq.Column(sq.Integer, primary_key=True)
    partner_id = sq.Column(sq.Integer, primary_key=True)

    def __str__(self):
        return f'{self.sender_id} :: vk.com/id{self.partner_id}'

class DbWorker:
    def __init__(self):
        create_data()
        self.engine = sq.create_engine(dsn)
        Base.metadata.create_all(bind=self.engine)
        self.session = Session(self.engine)

    def add_partner(self, sender_id, partner_id):
        """Добавление записи о просмоторенной анкете"""
        self.session.add(Viewed(sender_id=sender_id, partner_id=partner_id))
        self.session.commit()

    def wiev(self, sender_id, partner_id):
        """Проверка на совпадение"""
        return self.session.query(Viewed).filter(Viewed.sender_id==sender_id,
                                                 Viewed.partner_id==partner_id).first()

def create_data():
    """Создаём базу данных для хранения в ней данных о просмотренных анкетах"""
    default_user, default_base = 'postgres', 'postgres'
    conn = psycopg2.connect(database=default_base, user=default_user, 
                            password=password)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute("""CREATE DATABASE diplom;""")
    except Exception as e:
        # print(e) Если бот запущен впервые создаст базу данных, если
        # если не впервые - покажет ошибку
        conn.rollback()
    conn.close()

if __name__ == '__main__':
    my_bd = DbWorker()
    # my_bd.add_partner(123549, 1346978)
    # my_bd.add_partner(123549, 1346558)
    print(my_bd.wiev(123549, 1346978))
