from typing import Optional

from pydantic import BaseModel, field_validator

from schemas.PriceModel import PriceModel

class PhoneModel(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    price_currency: Optional[PriceModel] = None
    description: Optional[str] = None

    @field_validator('description', mode='before')
    def format_description(cls, value: str) -> str:
        return value.replace(" : ", "-") if value else "Not Available"

    # Config - used to configure the behavior of the data model, in my case - orm_mode=True to work with SQLAlchemy ORM
    # features
    class Config:
        orm_mode = True


class PhoneModelDTO(BaseModel):
    id: Optional[int] = None
    url: str
    title: str
    price_currency: PriceModel
    description: str

    @field_validator('description', mode='before')
    def format_description(cls, value: str) -> str:
        return value.replace(" : ", "-") if value else "Not Available"

    # Config - used to configure the behavior of the data model, in my case - orm_mode=True to work with SQLAlchemy ORM
    # features
    class Config:
        orm_mode = True
