import json
from json import JSONDecodeError
from bs4 import BeautifulSoup, PageElement
from datetime import timezone
import datetime
import re

from Constants import Constants
from PhoneEntityProcessor import price_str_to_float, construct_price_currency, switch_currency, filter_phones, \
    sum_prices
from Phone import PhoneEntity
from WebScraper import WebScraper
from FilteredPhones import FilteredPhones


def get_phones_html(web_scraper: WebScraper) -> list | PageElement:
    html_text: str = web_scraper.get_html_from_url()
    soup: BeautifulSoup = web_scraper.get_soup_from_html(html_text)
    products_html = web_scraper.get_tag_from_soup(soup, "div", "product-items-5 mt-3 ga-list")
    bs_products_html = BeautifulSoup(str(products_html), Constants.PARSER_TYPE)
    phones_html = web_scraper.get_tag_from_soup(bs_products_html, "div",
                                                "product-card bg-color-1c br-20 position-relative overflow-hidden h-100 product-item")
    return phones_html


def get_phone_from_html(web_scraper: WebScraper, item: PageElement) -> PhoneEntity:
    item_soup = BeautifulSoup(str(item), Constants.PARSER_TYPE)
    phone_item = web_scraper.get_tag_from_soup(item_soup, "a", class_name="d-block stretched-link text-white text-decoration-none product-link")[0]
    phone_dict = web_scraper.get_attributes_from_tag(phone_item, attributes=["href"], keys=["url"])
    data_ga4: str = phone_item.get("data-ga4")
    try:
        str_price: str = json.loads(data_ga4)["ecommerce"]["value"]
        currency: str = json.loads(data_ga4)["ecommerce"]["currency"]
        title: str = json.loads(data_ga4)["ecommerce"]["items"][0]["item_name"]
    except JSONDecodeError:
        str_price = re.search(r'"value":(\d+)', data_ga4).group(1)
        currency = re.search(r'"currency":"(\w+)"', data_ga4).group(1)
        title = re.search(r'"item_name":"(.+?)"', data_ga4).group(1)
    price = price_str_to_float(str_price)
    price_currency = construct_price_currency(price, currency)
    phone_dict["price_currency"] = price_currency
    phone_dict["title"] = title
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
    phone_entity = PhoneEntity.model_validate(phone_dict)
    return phone_entity


def process_phones(min_price: float, max_price: float, new_currency: str, phones: list[PhoneEntity]) -> FilteredPhones:
    phones = switch_currency(phones, new_currency)
    phones = filter_phones(min_price, max_price, phones)
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    filtered_phones = FilteredPhones(phones, sum_prices(phones), utc_timestamp)
    return filtered_phones

