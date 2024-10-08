import json
from urllib.request import Request
from Phone import PhoneEntity
from bs4 import BeautifulSoup
from CurrencyConvertor import construct_price_currency
from UrllibHTMLRequester import UrllibHTMLRequester
from PhoneEntityProcessor import price_str_to_float, validate_description, switch_currency, filter_phones, sum_prices
from WebScraper import WebScraper
from TLSHTMLRequester import TLSHTMLRequester
from datetime import timezone
import datetime
from FilteredPhones import FilteredPhones


def start_process(web_scraper: WebScraper) -> FilteredPhones:
    html_text: str = web_scraper.get_html_from_url()
    soup: BeautifulSoup = web_scraper.get_soup_from_html(html_text)
    items: list = web_scraper.get_tag_from_soup(soup, "a", "ga-item")
    set_items = set(items)
    phones: list[PhoneEntity] = []
    for item in set_items:
        phone: dict = web_scraper.get_attributes_from_tag(item, "href", "title")
        data_ga4: str = item["data-ga4"]
        str_price: str = json.loads(data_ga4)["ecommerce"]["value"]

        # POINT 5 - VALIDATION OF PRICE
        price = price_str_to_float(str_price)

        price_currency = construct_price_currency(price, json.loads(data_ga4)["ecommerce"]["currency"])
        phone["price_currency"] = price_currency

        # Point 4 - SCRAP HREF AND ADD AN ATTRIBUTE TO PHONE
        request: Request = web_scraper.create_request(custom_url=phone["href"])
        html_text_phone: str = web_scraper.get_html_from_url(request)
        soup_phone: BeautifulSoup = web_scraper.get_soup_from_html(html_text_phone)
        feature_soup: list = web_scraper.get_tag_from_soup(soup_phone.find("div", class_="main-description"),
                                                           "li", class_name="char_all")
        validate_description(feature_soup, phone)
        phone_entity = PhoneEntity(phone.get("href"), phone.get("title"), phone.get("price_currency"),
                                   phone.get("description"))
        phones.append(phone_entity)
        print(phone_entity)

    # POINT 6 - SWITCH CURRENCY, FILTER BY PRICE
    new_currency = "EUR"
    phones = switch_currency(phones, new_currency)

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
    return filtered_phones


if __name__ == '__main__':
    # urllib_web_scraper: UrllibHTMLRequester = UrllibHTMLRequester()
    # start_process(urllib_web_scraper)

    tls_web_scraper: TLSHTMLRequester = TLSHTMLRequester()
    start_process(tls_web_scraper)
