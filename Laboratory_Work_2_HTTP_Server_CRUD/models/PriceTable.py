from sqlalchemy import Column, Integer, Float, String

from ..database.connection import Base


# From connection import Base that is the base model for ORM models.
class PriceTableModel(Base):
    # Define the name of the table
    __tablename__ = "price"

    # Define the columns of the table
    id = Column(Integer, primary_key=True, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
