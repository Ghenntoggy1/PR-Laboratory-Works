from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from database.connection import Base, engine


# From connection import Base that is the base model for ORM models.
class PhoneTableModel(Base):
    # Define the name of the table
    __tablename__ = "phone"

    # Define the columns of the table
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # Define the foreign key for the price_currency column
    price_currency_id = Column(Integer, ForeignKey("price.id"), nullable=False)
    price_currency = relationship("PriceTableModel", backref=backref("phone", uselist=False))


def create_table():
    PhoneTableModel.metadata.create_all(bind=engine)

