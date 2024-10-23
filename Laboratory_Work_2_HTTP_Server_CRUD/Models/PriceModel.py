from pydantic import BaseModel, field_validator


class PriceModel(BaseModel):
    price: float
    currency: str

    @field_validator('price', mode='before')
    def format_price(cls, value: float) -> float:
        return value if 0.0 <= value else 0.0
