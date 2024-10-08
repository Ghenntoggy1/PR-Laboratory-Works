import re
from CurrencyConvertor import CurrencyConvertor
import functools
from Phone import PhoneEntity


# POINT 5 - VALIDATION OF PRICE
def price_str_to_float(price_str: str) -> float:
    try:
        price = float(price_str)
    except ValueError:
        price = 0.0
    return price


# POINT 5 - VALIDATION OF DESCRIPTION
def validate_description(feature_soup: list, phone: dict) -> None:
    for feature in feature_soup:
        feature_text = feature.text.strip()
        if "Tehnologie de fabricație" in feature_text:
            description = re.sub(r"\s+", " ",
                                 feature_text.replace("Tehnologie de fabricație", "Fabrication Technology"))
            phone["description"] = description
            break
        else:
            phone["description"] = "Fabrication Technology: Not Available"


# POINT 6 - SWITCH CURRENCY
def switch_currency(phone_entity_list: list, new_currency: str) -> list:
    print(f"Switching currency to {new_currency}")
    currency_convertor = CurrencyConvertor()
    if new_currency not in currency_convertor.get_currencies():
        print(f"Currency {new_currency} not supported")
        return phone_entity_list

    def convert_phone_currency(phone_entity):
        current_currency = phone_entity.price.get("currency")
        current_price = phone_entity.price.get("price")
        new_price = currency_convertor.convert(current_price, current_currency, new_currency)
        phone_entity.price["price"] = new_price
        phone_entity.price["currency"] = new_currency
        return phone_entity
    phone_entity_list = list(map(convert_phone_currency, phone_entity_list))
    return phone_entity_list


# POINT 6 - FILTER BY PRICE
def filter_phones(min_price: float, max_price: float, phone_list: list) -> list:
    print(f"Phones with price between {min_price} and {max_price}")
    phone_new_list = list(filter(lambda phone_entity: min_price <= phone_entity.price.get("price") <= max_price,
                                 phone_list))
    for phone in phone_new_list:
        print(phone.__repr__())
    return phone_new_list


# POINT 6 - SUM PRICES
def sum_prices(phone_list: list) -> float:
    print("Sum of prices of the Products")
    if not phone_list:
        print("No phones to sum")
        return 0.0

    return functools.reduce(
        lambda pe1, pe2: pe1 + pe2,
        map(lambda phone: phone.price.get("price"), phone_list)
    )

