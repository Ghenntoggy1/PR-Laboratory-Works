import json
import re
from json import JSONDecodeError
from typing import Tuple, List
from urllib.request import Request

import requests

from Laboratory_Work_1_Scraper_HTTP_Requests.Constants import Constants
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
    products_html = web_scraper.get_tag_from_soup(soup, "div", "product-items-5 mt-3")
    bs_products_html = BeautifulSoup(str(products_html), Constants.PARSER_TYPE)
    phones_html = web_scraper.get_tag_from_soup(bs_products_html, "div", "product-card bg-color-1c br-20 position-relative overflow-hidden h-100")
    phones: list[PhoneEntity] = []
    for item in phones_html:
        item_soup = BeautifulSoup(str(item), Constants.PARSER_TYPE)
        phone_item = web_scraper.get_tag_from_soup(item_soup, "a", "d-block stretched-link text-white text-decoration-none")[0]
        phone_dict = web_scraper.get_attributes_from_tag(phone_item, attributes=["href"], keys=["url"])
        if phone_dict.get("href") in [phone_entity.url for phone_entity in phones]:
            continue
        data_ga4: str = phone_item.get("data-ga4")
        try:
            str_price: str = json.loads(data_ga4)["ecommerce"]["value"]
            currency: str = json.loads(data_ga4)["ecommerce"]["currency"]
            title: str = json.loads(data_ga4)["ecommerce"]["items"][0]["item_name"]
        except JSONDecodeError:
            str_price = re.search(r'"value":(\d+)', data_ga4).group(1)
            currency = re.search(r'"currency":"(\w+)"', data_ga4).group(1)
            title = re.search(r'"item_name":"(.+?)"', data_ga4).group(1)
        # POINT 5 - VALIDATION OF PRICE
        price = price_str_to_float(str_price)

        price_currency = construct_price_currency(price, currency)
        phone_dict["price_currency"] = price_currency
        phone_dict["title"] = title

        # Point 4 - SCRAP HREF AND ADD AN ATTRIBUTE TO PHONE
        request = web_scraper.create_request(custom_url=phone_dict["url"])
        html_text_phone: str = web_scraper.get_html_from_url(request)
        soup_phone: BeautifulSoup = web_scraper.get_soup_from_html(html_text_phone)
        html_description = web_scraper.get_tag_from_soup(soup_phone, "div", "row row-cols-1 row-cols-md-1 row-cols-xl-2 g-2 g-sm-3")
        soup_description = BeautifulSoup(str(html_description), Constants.PARSER_TYPE)
        html_divs = web_scraper.get_tag_from_soup(soup_description, "div", "col")
        soup_div = BeautifulSoup(str(html_divs[2]), Constants.PARSER_TYPE)
        html_processor = web_scraper.get_tag_from_soup(soup_div, "tr", "d-flex")
        soup_processor = BeautifulSoup(str(html_processor), Constants.PARSER_TYPE)
        text_desc: str = web_scraper.get_tag_from_soup(soup_processor, "td", "pt-2 pe-4 w-100 mw-300")[0].text
        text_value: str = web_scraper.get_tag_from_soup(soup_processor, "td", "pt-2 pe-4 w-100")[0].text
        value = f"{text_desc.strip()} : {text_value.strip()}"
        phone_dict["description"] = value
    #     feature_soup: list = web_scraper.get_tag_from_soup(soup_phone.find("div", class_="main-description"),
    #                                                        "li", class_name="char_all")
    #     validate_description(value, phone_dict)
    #     phone_entity = PhoneEntity(phone_dict.get("href"), phone_dict.get("title"), phone_dict.get("price_currency"),
    #                                phone_dict.get("description"))
        phone_entity = PhoneEntity.model_validate(phone_dict)
        phones.append(phone_entity)
        print(phone_entity)

    # POINT 6 - SWITCH CURRENCY, FILTER BY PRICE
    new_currency = "EUR"
    phones = switch_currency(phones, new_currency)
    for phone in phones:
        print(phone)
    all_phones_TCP = phones.copy()
    min_price = 400
    max_price = 600
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
        phone_json_serialized = serialize_phone_JSON(phone.to_dict())
        print(phone_json_serialized)

    # json_file = "phones.json"
    # with open(json_file, "w") as file:
    #     json.dump([phone.to_dict() for phone in all_phones], file, indent=4)
    #
    # json_file_price = "prices.json"
    # with open(json_file_price, "w") as file:
    #     json.dump([phone.price_currency.model_dump() for phone in all_phones], file, indent=4)

    print("SERIALIZED JSON LIST OBJECTS")
    phone_dicts = []
    for phone in all_phones_TCP:
        phone_dicts.append(phone.to_dict())
    JSON_LIST_DATA = serialize_phone_JSON(phone_dicts)
    print(JSON_LIST_DATA.decode("utf-8"))

    print("SERIALIZED XML OBJECTS")
    for phone in all_phones_TCP:
        phone_xml_serialized = serialize_phone_XML(phone.to_dict())
        print(phone_xml_serialized)

    print("SERIALIZED XML LIST OBJECTS")
    phone_dicts = []
    for phone in all_phones_TCP:
        phone_dicts.append(phone.to_dict())
    XML_LIST_DATA = serialize_phone_XML(phone_dicts)
    print(XML_LIST_DATA)

    print("SERIALIZED LINERS OBJECTS")
    for phone in all_phones_TCP:
        phone_liners_serialized = serialize_phone_LINERS(phone.to_dict())
        print(phone_liners_serialized)

    print("SERIALIZED LINERS LIST OBJECTS")
    phone_dicts = []
    for phone in all_phones_TCP:
        phone_dicts.append(phone.to_dict())
    serialized_linears_phones = serialize_phone_LINERS(phone_dicts)
    print(serialized_linears_phones)
    print(type(serialized_linears_phones))

    print("DESERIALIZED LINERS LIST OBJECTS")
    print(deserialize_list_phones_LINERS(serialized_linears_phones))

    # data_json = JSON_LIST_DATA
    # data_xml = XML_LIST_DATA
    #
    # url = 'http://localhost:8000/upload'
    #
    # response_json = requests.post(url, data=data_json, headers={'Content-Type': 'application/json'})
    # print('JSON Response:', response_json.status_code, response_json.text)
    #
    # response_xml = requests.post(url, data=data_xml, headers={'Content-Type': 'application/xml'})
    # print('XML Response:', response_xml.status_code, response_xml.text)
    #
    # while True:
    #     # 503
    #     password = input("Enter password: ")
    #     # 201
    #     username = input("Enter username: ")
    #     response_json = requests.post(url, data=data_json, headers={'Content-Type': 'application/json'},
    #                                   auth=(username, password))
    #
    #     print('JSON Response:', response_json.status_code, response_json.text)
    #
    #     response_xml = requests.post(url, data=data_xml, headers={'Content-Type': 'application/xml'},
    #                                  auth=(username, password))
    #     print('XML Response:', response_xml.status_code, response_xml.text)
    #
    #     if response_json.status_code == 200 and response_xml.status_code == 200:
    #         break
