from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DATABASE_URL")

# Load Data Base URL
if database_url:
    print("Database link loaded")
else:
    print("Link not loaded for db connection")

engine = create_engine(database_url, echo=True)


# Initiating Data Base core workflow through loading all models
def Initiate_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
