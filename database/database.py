from sqlmodel import Session, create_engine
from os.path import isfile
#from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import os,sys

    #engine = create_engine("postgresql:///?User=postgres&Password=admin&Database=postgres&Server=127.0.0.1&Port=5432")
    #engine = create_engine('sqlite:///database/deudas.sqlite', connect_args={'check_same_thread': False})
    #engine = create_engine("postgresql:///?User=postgres&Password=root&Database=debtman&Server=127.0.0.1&Port=5432")
    
    #engine = create_engine('postgresql+psycopg2://postgres:root@localhost/debtmanager')

try:
   
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    engine = create_engine(DATABASE_URL)
    
    if engine:
        conn = engine.connect()
        print("--------------------- Connection success to database: debtmanager --------------------------------")
   
except SQLAlchemyError:
    print("Error en la base de datos, revise el servicio de base de datos")
    sys.exit()
    
except ConnectionError:
    print("Error en la base de datos, revise el servicio de base de datos")
    sys.exit()
    
def get_session():
    with Session(engine) as session:
        #disable if you are using postgresql
        #session.exec('PRAGMA foreign_keys=ON;')
        yield session
        
