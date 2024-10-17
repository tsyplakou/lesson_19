from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from constants import DB_CONNECTION

engine = create_engine(
    'postgresql://{user}:{password}@{host}:5432/{dbname}'.format(**DB_CONNECTION),
)

Session = sessionmaker(bind=engine)



@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
