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
    if not phone_list:
        print("No phones to sum")
        return 0.0

    return functools.reduce(
        lambda pe1, pe2: pe1 + pe2,
        map(lambda phone: phone.price.get("price"), phone_list)
    )


def serialize_phone_JSON(object) -> bytearray:
    # METHOD 1:
    # phone_str = (f'{{"url": "{phone.url}", '
    #              f'"title": "{phone.title}", '
    #              f'"priceTag": {{"currency": "{phone.price.get("currency")}", "price": {phone.price.get("price")}}}, '
    #              f'"description": "{phone.description}"}}')

    # METHOD 2:
    phone_str = ""

    if isinstance(object, dict):
        pairs = []
        for key, value in object.items():
            pairs.append(f'{serialize_phone_JSON(key).decode("utf-8")}:{serialize_phone_JSON(value).decode("utf-8")}')
        phone_str = "{" + ", ".join(pairs) + "}"
    elif isinstance(object, list):
        items = [serialize_phone_JSON(item).decode("utf-8") for item in object]
        phone_str = "[" + ",".join(items) + "]"
    elif isinstance(object, str):
        phone_str = f'"{object}"'
    elif isinstance(object, (int, float)):
        phone_str = str(object)
    elif isinstance(object, bool):
        phone_str = "true" if object else "false"
    elif object is None:
        phone_str = "null"

    return bytearray(phone_str.encode("utf-8"))


def serialize_list_phones_JSON(phones: list[PhoneEntity]) -> bytearray:
    phone_str = serialize_phone_JSON(phones)
    return phone_str


def serialize_phone_XML(object) -> bytearray:
    # Method 1:
    # phone_str = (f'<phone>'
    #              f'<url>{phone.url}</url>'
    #              f'<title>{phone.title}</title>'
    #              f'<priceTag>'
    #              f'<currency>{phone.price.get("currency")}</currency>'
    #              f'<price>{phone.price.get("price")}</price>'
    #              f'</priceTag>'
    #              f'<description>{phone.description}</description>'
    #              f'</phone>')

    # Method 2:
    phone_str = ""
    if isinstance(object, dict):
        tags = []
        for key, value in object.items():
            tags.append(f'<{key}>{serialize_phone_XML(value).decode("utf-8")}</{key}>')
        phone_str = "<phone>" + "".join(tags) + "</phone>"
    elif isinstance(object, list):
        phone_str = "<phones>"
        for item in object:
            phone_str += serialize_phone_XML(item).decode("utf-8")
        phone_str += "</phones>"
    elif isinstance(object, str):
        phone_str = object
    elif isinstance(object, (int, float)):
        phone_str = str(object)
    elif isinstance(object, bool):
        phone_str = "true" if object else "false"
    elif object is None:
        phone_str = ""

    return bytearray(phone_str.encode("utf-8"))


def serialize_list_phones_XML(phones: list[PhoneEntity]) -> bytearray:
    phone_str = f'<phones>{"".join([serialize_phone_XML(phone).decode("utf-8") for phone in phones])}</phones>'
    return bytearray(phone_str.encode("utf-8"))


def serialize_phone_LINERS(phone: PhoneEntity) -> bytearray:
    phone_str = (f'|= '
                 f'|+ url - {phone.url} +| '
                 f'|+ title - {phone.title} +| '
                 f'|+ priceObj - |= '
                 f'|+ currency - {phone.price.get("currency")} +| '
                 f'|+ price - {phone.price.get("price")} +| '
                 f'=| +| '
                 f'|+ description - {phone.description} +| =|')
    print(phone_str)
    return bytearray(phone_str.encode("utf-8"))


def serialize_list_phones_LINERS(phones: list[PhoneEntity]) -> bytearray:
    phone_str = f'[{"!".join([serialize_phone_LINERS(phone).decode("utf-8") for phone in phones])}]'
    return bytearray(phone_str.encode("utf-8"))

def deserialize_phone_LINERS(phone_str: bytearray) -> PhoneEntity:
    # Decode bytearray to string
    data_str = phone_str.decode("utf-8")

    # |= =| delimiter
    dict_str = {}
    object_str = data_str[data_str.find("|= ") + 3:-1]
    start_index = object_str.find("|+ ") + 3
    end_index = object_str.find(" - ", start_index)
    prev_key = ""
    while start_index < len(object_str):
        old_copy = dict_str.copy()
        if prev_key.endswith("Obj"):
            key = prev_key
        else:
            key = object_str[start_index:end_index].replace(" ", "")
        if object_str.find(" +|", end_index + 3) < object_str.find(" |=", end_index + 3) or not key.endswith("Obj"):
            start_index = end_index + 3
            end_index = object_str.find(" +|", start_index)
            value = object_str[start_index:end_index]
            dict_str[key] = value
            start_index = object_str.find("|+ ", end_index + 3) + 3
            end_index = object_str.find(" - ", start_index)
            if old_copy == dict_str:
                break
        elif object_str.find(" |=", end_index + 3) < object_str.find(" +|", end_index + 3):
            flag = True
            if object_str.find(" |=", end_index + 3) == -1:
                if object_str[object_str.find("|+ ", end_index + 3) + 3:object_str.find(" - ", start_index)] == prev_key:
                    start_index = object_str.find("|+ ", end_index + 3) + 3
                    end_index = object_str.find(" - ", start_index)
                else:
                    flag = False
                    pass
            else:
                start_index = object_str.find(" |+", end_index + 3) + 3
                end_index = object_str.find(" - ", start_index)
            inner_key = object_str[start_index:end_index]
            start_index = object_str.find(" - ", end_index) + 3
            end_index = object_str.find(" +|", start_index)
            inner_value = object_str[start_index:end_index]
            if key in dict_str:
                dict_str[key][inner_key] = inner_value
            else:
                dict_str[key] = {}
                dict_str[key][inner_key] = inner_value
            start_index = object_str.find("|+ ", end_index) + 3
            end_index = object_str.find(" - ", start_index)
            if flag:
                prev_key = key
            else:
                prev_key = ""
        else:
            dict_str[key] = {}
            start_index = object_str.find("|+", start_index) + 3
            end_index = object_str.find(" - ", start_index)
            inner_object_str = object_str[start_index:end_index]

    # Create and return PhoneEntity
    return PhoneEntity(url=dict_str.get("url"), title=dict_str.get("title"), price=dict_str.get("priceObj"), description=dict_str.get("description"))


def deserialize_list_phones_LINERS(phones_str: bytearray) -> list[PhoneEntity]:
    # Decode bytearray to string
    data_str = phones_str.decode("utf-8")
    data_str_list = data_str.split("!")
    phones = []
    for data in data_str_list:
        phone_data = deserialize_phone_LINERS(bytearray(data.encode("utf-8")))
        phone_entity = PhoneEntity(url=phone_data.url, title=phone_data.title, price=phone_data.price, description=phone_data.description)
        phones.append(phone_entity)
        print(phone_entity)
    return phones

