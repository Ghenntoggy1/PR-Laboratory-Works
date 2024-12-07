import os

from dotenv import load_dotenv

# Import the necessary modules from the SQLAlchemy library - ORM framework
from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

# IF RUN FROM PYCHARM
# load_dotenv(dotenv_path=".env")

# Get the database connection URL from the environment variables
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_CONTAINER_NAME = os.getenv("DATABASE_CONTAINER_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_PORT = os.getenv("DATABASE_PORT")
# DATABASE_CONNECTION_URL = f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_CONTAINER_NAME}:{DATABASE_PORT}/{DATABASE_NAME}"
DATABASE_CONNECTION_URL = f"postgresql+psycopg2://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@localhost:5454/{DATABASE_NAME}"

# Create the database engine using the connection URL - to Docker container
# Engine is factory that can create new database connections for us, which also holds onto connections inside of a
# Connection Pool for fast reuse
print(DATABASE_CONNECTION_URL)
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
