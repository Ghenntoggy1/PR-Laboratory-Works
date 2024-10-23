from pydantic import BaseModel, field_validator


# class PhoneEntity(BaseModel):
#     # def __init__(self, url: str, title: str, price: dict, description: str):
#     #     self.url = url
#     #     self.title = title
#     #     self.price = price
#     #     self.description = description.replace(" : ", ":") if description is not None else "Not Available"
#
#     url: str
#     title: str
#     price_currency: dict
#     description: str
#
#     @field_validator('description', mode='before')
#     def format_description(cls, value):
#         return value.replace(" : ", ":") if value else "Not Available"
#
#     def __repr__(self):
#         return f"PhoneEntity({self.url}, {self.title}, {self.price}, {self.description})"
#
#     def __str__(self):
#         return (f"Phone {self.title} with price: {self.price.get('price')} {self.price.get('currency')}"
#                 f" and description: {self.description}")
#
#     def __dict__(self):
#         return {
#             "url": self.url,
#             "title": self.title,
#             "price_currency": self.price,
#             "description": self.description
#         }


class Price(BaseModel):
    price: float
    currency: str

class PhoneEntity(BaseModel):
    url: str
    title: str
    price_currency: Price
    description: str

    @field_validator('description', mode='before')
    def format_description(cls, value):
        return value.replace(" : ", "-") if value else "Not Available"

    def __repr__(self):
        return f"PhoneEntity(url={self.url}, title={self.title}, price={self.price_currency}, description={self.description})"

    def __str__(self):
        return (f"Phone {self.title} with price: {self.price_currency.price} {self.price_currency.currency}"
                f" and description: {self.description}")

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "price_currency": self.price_currency.model_dump(),
            "description": self.description
        }