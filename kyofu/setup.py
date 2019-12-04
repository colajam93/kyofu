def setup_database_connection():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('mysql+mysqldb://kyofu:kyofu@172.17.0.1:3306/kyofu?charset=utf8mb4')
    session = sessionmaker(bind=engine)()
    return engine, session
