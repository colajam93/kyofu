def setup_database_connection():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from kyofu.config import DB_URL, SQLALCHEMY_ENGINE_ECHO

    engine = create_engine(DB_URL, echo=SQLALCHEMY_ENGINE_ECHO)
    session = sessionmaker(bind=engine)()
    return engine, session
