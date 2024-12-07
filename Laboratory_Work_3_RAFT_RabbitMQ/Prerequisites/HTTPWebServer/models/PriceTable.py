from sqlalchemy import Column, Integer, Float, String

# from ..database.connection import Base, engine

from database.connection import Base, engine

# From connection import Base that is the base model for ORM models.
class PriceTableModel(Base):
    # Define the name of the table
    __tablename__ = "price"

    # Define the columns of the table
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)


def create_table():
    PriceTableModel.metadata.create_all(bind=engine)
