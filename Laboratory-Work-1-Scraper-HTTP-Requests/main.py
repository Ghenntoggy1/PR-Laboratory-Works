import json
import re
from urllib.request import Request
from Phone import PhoneEntity
from bs4 import BeautifulSoup

from WebScraper import WebScraper

if __name__ == '__main__':
    web_scraper: WebScraper = WebScraper()
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
        try:
            price = float(str_price)
        except ValueError:
            price = 0.0

        price_currency = {
            "currency": json.loads(data_ga4)["ecommerce"]["currency"],
            "price": price
        }
        phone["price_currency"] = price_currency

        # Point 4 - SCRAP HREF AND ADD AN ATTRIBUTE TO PHONE
        request: Request = web_scraper.create_request(custom_url=phone["href"])
        html_text_phone: str = web_scraper.get_html_from_url(request)
        soup_phone: BeautifulSoup = web_scraper.get_soup_from_html(html_text_phone)
        feature_soup: list = web_scraper.get_tag_from_soup(soup_phone.find("div", class_="main-description"), "li", class_name="char_all")
        for feature in feature_soup:
            feature_text = feature.text.strip()

            # POINT 5 - VALIDATION OF DESCRIPTION
            if "Tehnologie de fabricație" in feature_text:
                print(feature_text)
                description = re.sub(r"\s+", " ", feature_text.replace("Tehnologie de fabricație", "Fabrication Technology"))
                phone["description"] = description
                break
            else:
                phone["description"] = "Fabrication Technology: Not Available"
        phone_entity = PhoneEntity(phone.get("href"), phone.get("title"), phone.get("price_currency"), phone.get("description"))
        phones.append(phone_entity)
        print(phone_entity)
    print(phones)