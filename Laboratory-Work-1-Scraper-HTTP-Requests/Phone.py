import re


class PhoneEntity:
    def __init__(self, url: str, title: str, price: dict, description: str):
        self.url = url
        self.title = title
        self.price = price
        self.description = re.sub(" : ", ":", description)

    def __repr__(self):
        return f"PhoneEntity({self.url}, {self.title}, {self.price}, {self.description})"
