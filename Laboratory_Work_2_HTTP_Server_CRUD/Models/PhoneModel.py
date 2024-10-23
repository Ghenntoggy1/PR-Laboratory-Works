from pydantic import BaseModel, field_validator

from Price import PriceEntity


class PhoneEntity(BaseModel):
    url: str
    title: str
    price_currency: PriceEntity
    description: str

    @field_validator('description', mode='before')
    def format_description(cls, value) -> str:
        return value.replace(" : ", "-") if value else "Not Available"
