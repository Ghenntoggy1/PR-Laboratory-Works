from typing import Optional

from pydantic import BaseModel, field_validator


class PriceModel(BaseModel):
    price: Optional[float] = None
    currency: Optional[str] = None

    # @field_validator('price', mode='before')
    # def format_price(cls, value: float) -> float:
    #     return value if 0.0 <= value else 0.0

    # Config - used to configure the behavior of the data model, in my case - orm_mode=True to work with SQLAlchemy ORM
    # features
    class Config:
        orm_mode = True


class PriceModelDTO(BaseModel):
    id: int
    price: float
    currency: str

    # @field_validator('price', mode='before')
    # def format_price(cls, value: float) -> float:
    #     return value if 0.0 <= value else 0.0

    # Config - used to configure the behavior of the data model, in my case - orm_mode=True to work with SQLAlchemy ORM
    # features
    class Config:
        orm_mode = True
