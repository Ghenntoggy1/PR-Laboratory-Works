import re


class PhoneEntity:
    def __init__(self, url: str, title: str, price: dict, description: str):
        self.url = url
        self.title = title
        self.price = price
        self.description = description.replace(" : ", ":")

    def __repr__(self):
        return f"PhoneEntity({self.url}, {self.title}, {self.price}, {self.description})"

    def __str__(self):
        return (f"Phone {self.title} with price: {self.price.get('price')} {self.price.get('currency')}"
                f" and description: {self.description}")

    def __dict__(self):
        return {
            "url": self.url,
            "title": self.title,
            "price_currency": self.price,
            "description": self.description
        }
