from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..connection import Base


# From connection import Base that is the base model for ORM models.
class PhoneTableModel(Base):
    # Define the name of the table
    __table__ = "phone"

    # Define the columns of the table
    id = Column(Integer, primary_key=True, nullable=False)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    price_currency_id = Column(Integer, ForeignKey("price.id"), nullable=False)
    price_currency = relationship("PriceTableModel")
    description = Column(String, nullable=False)
