from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , DeclarativeBase 
from dotenv import load_dotenv
import os

load_dotenv()



#it know how to open a connection to the database
#it create ready connection(session) that is ready to borrow
engine = create_engine(os.getenv("DATABASE_URL"))

#it dosn't create session 
#it create a factory that when it called "SessionLocal()" it create session 
SessionLocal = sessionmaker(bind=engine)

#every table(python class) you define that inherit from 
#that how SQL alchemy knows "this python class is a database table"
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal() #open a session
    try:
        yield db #hand it to whoever ask it 
    finally:
        db.close() #always close it when done, even if it crashes