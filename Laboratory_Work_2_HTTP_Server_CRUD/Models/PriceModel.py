from pydantic import BaseModel, field_validator


class PriceEntity(BaseModel):
    price: float
    currency: str

    @field_validator('price', mode='before')
    def format_price(cls, value) -> float:
        return value if 0.0 <= value else 0.0
