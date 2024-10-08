import json
import re
from json import JSONDecodeError
from typing import Tuple, List
from urllib.request import Request

import requests

from Phone import PhoneEntity
from bs4 import BeautifulSoup
from CurrencyConvertor import construct_price_currency
from UrllibHTMLRequester import UrllibHTMLRequester
from PhoneEntityProcessor import *
from WebScraper import WebScraper
from TCPHTMLRequester import TCPHTMLRequester
from datetime import timezone
import datetime
from FilteredPhones import FilteredPhones


def start_process(web_scraper: WebScraper) -> tuple[FilteredPhones, list[PhoneEntity]]:
    html_text: str = web_scraper.get_html_from_url()
    soup: BeautifulSoup = web_scraper.get_soup_from_html(html_text)
    items: list = web_scraper.get_tag_from_soup(soup, "a", "ga-item")
    set_items = set(items)
    phones: list[PhoneEntity] = []
    for item in set_items:
        phone: dict = web_scraper.get_attributes_from_tag(item, "href", "title")
        if phone.get("href") in [phone_entity.url for phone_entity in phones]:
            continue
        data_ga4: str = item["data-ga4"]
        try:
            str_price: str = json.loads(data_ga4)["ecommerce"]["value"]
            currency: str = json.loads(data_ga4)["ecommerce"]["currency"]
        except JSONDecodeError:
            str_price = re.search(r'"value":(\d+)', data_ga4).group(1)
            currency = re.search(r'"currency":"(\w+)"', data_ga4).group(1)
        # POINT 5 - VALIDATION OF PRICE
        price = price_str_to_float(str_price)

        price_currency = construct_price_currency(price, currency)
        phone["price_currency"] = price_currency

        # Point 4 - SCRAP HREF AND ADD AN ATTRIBUTE TO PHONE
        request = web_scraper.create_request(custom_url=phone["href"])
        html_text_phone: str = web_scraper.get_html_from_url(request)
        soup_phone: BeautifulSoup = web_scraper.get_soup_from_html(html_text_phone)
        feature_soup: list = web_scraper.get_tag_from_soup(soup_phone.find("div", class_="main-description"),
                                                           "li", class_name="char_all")
        validate_description(feature_soup, phone)
        phone_entity = PhoneEntity(phone.get("href"), phone.get("title"), phone.get("price_currency"),
                                   phone.get("description"))
        phones.append(phone_entity)
        print(phone_entity)
        # # TODO DELETE
        # break

    # POINT 6 - SWITCH CURRENCY, FILTER BY PRICE
    new_currency = "EUR"
    phones = switch_currency(phones, new_currency)
    all_phones_TCP = phones.copy()
    min_price = 300
    max_price = 350
    phones = filter_phones(min_price, max_price, phones)

    print("Sum of filtered Products:", sum_prices(phones), new_currency)
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    print("UTC Timestamp:", utc_timestamp)
    filtered_phones = FilteredPhones(phones, sum_prices(phones), utc_timestamp)
    print(filtered_phones.__repr__())
    return filtered_phones, all_phones_TCP


if __name__ == '__main__':
    print("Web Scraping with Urllib")
    urllib_web_scraper: UrllibHTMLRequester = UrllibHTMLRequester()
    filtered_phones, all_phones = start_process(urllib_web_scraper)

    print("Web Scraping with TCP with SSL")
    tls_web_scraper: TCPHTMLRequester = TCPHTMLRequester()
    filtered_phones_TCP, all_phones_TCP = start_process(tls_web_scraper)
    print("SERIALIZED JSON OBJECTS")
    for phone in all_phones_TCP:
        phone_json_serialized = serialize_phone_JSON(phone.__dict__())
        print(phone_json_serialized)

    print("SERIALIZED JSON LIST OBJECTS")
    phone_dicts = []
    for phone in all_phones_TCP:
        phone_dicts.append(phone.__dict__())
    JSON_LIST_DATA = serialize_phone_JSON(phone_dicts)
    print(JSON_LIST_DATA.decode("utf-8"))

    print("SERIALIZED XML OBJECTS")
    for phone in all_phones_TCP:
        phone_xml_serialized = serialize_phone_XML(phone.__dict__())
        print(phone_xml_serialized)

    print("SERIALIZED XML LIST OBJECTS")
    phone_dicts = []
    for phone in all_phones_TCP:
        phone_dicts.append(phone.__dict__())
    XML_LIST_DATA = serialize_phone_XML(phone_dicts)
    print(XML_LIST_DATA)

    print("SERIALIZED LINERS OBJECTS")
    for phone in all_phones_TCP:
        phone_liners_serialized = serialize_phone_LINERS(phone)
        print(phone_liners_serialized)

    print("SERIALIZED LINERS LIST OBJECTS")
    serialized_linears_phones = serialize_list_phones_LINERS(all_phones_TCP)
    print(serialized_linears_phones)
    print(type(serialized_linears_phones))

    print("DESERIALIZED LINERS LIST OBJECTS")
    print(deserialize_list_phones_LINERS(serialized_linears_phones))

    data_json = JSON_LIST_DATA
    data_xml = XML_LIST_DATA

    url = 'http://localhost:8000/upload'

    response_json = requests.post(url, data=data_json, headers={'Content-Type': 'application/json'})
    print('JSON Response:', response_json.status_code, response_json.text)

    response_xml = requests.post(url, data=data_xml, headers={'Content-Type': 'application/xml'})
    print('XML Response:', response_xml.status_code, response_xml.text)

    while True:
        # 404
        password = input("Enter password: ")
        # 307
        username = input("Enter username: ")
        response_json = requests.post(url, data=data_json, headers={'Content-Type': 'application/json'},
                                      auth=(username, password))

        print('JSON Response:', response_json.status_code, response_json.text)

        response_xml = requests.post(url, data=data_xml, headers={'Content-Type': 'application/xml'},
                                     auth=(username, password))
        print('XML Response:', response_xml.status_code, response_xml.text)

        if response_json.status_code == 200 and response_xml.status_code == 200:
            break
