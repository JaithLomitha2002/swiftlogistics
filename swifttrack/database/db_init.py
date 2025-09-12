from sqlalchemy import create_engine
from models import Base

DATABASE_URL = 'postgresql+psycopg2://postgres:mycoc1@localhost:5432/swifttrack'

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
