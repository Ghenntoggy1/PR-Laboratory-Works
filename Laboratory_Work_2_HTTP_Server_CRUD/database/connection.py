import os

from dotenv import load_dotenv

# Import the necessary modules from the SQLAlchemy library - ORM framework
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env file
load_dotenv()

# Get the database connection URL from the environment variables
DATABASE_CONNECTION_URL = os.getenv("DATABASE_CONNECTION_URL")

# Create the database engine using the connection URL - to Docker container
# Engine is factory that can create new database connections for us, which also holds onto connections inside of a
# Connection Pool for fast reuse
engine = create_engine(DATABASE_CONNECTION_URL)

# Create a session object - Session establishes all conversations with the database, it will permit me to use the ORM
# framework to define the schema of the database and query it not using SQL queries, but using ORM methods
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for the ORM models - Base class will be used to create the models of the database
Base = declarative_base()


# Function to get the database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
