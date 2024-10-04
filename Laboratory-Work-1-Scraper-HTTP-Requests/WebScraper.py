# Web Scraper class
import json

import requests

from Constants import Constants
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self):
        self.url = Constants.URL_WEBSITE

    def create_request(self, custom_url: str = Constants.URL_WEBSITE, custom_headers=Constants.HEADERS) -> Request:
        return Request(
            url=custom_url,
            headers=custom_headers
        )

    def get_html_from_url(self, request: Request = None) -> str:
        # POINT 2 - GET REQUEST TO DARWIN PHONES PAGE
        # respone = requests.get(url=self.url, headers=Constants.HEADERS)
        # html_bytes = respone.content
        if request is None:
            request = self.create_request()

        # USE ANOTHER LIBRARY
        page = urlopen(request)
        html_bytes = page.read()
        return html_bytes.decode(Constants.DECODE_FORMAT)

    # POINT 3 - USE OF BEAUTIFULSOUP TO PARSE HTML CONTENT
    def get_soup_from_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, Constants.PARSER_TYPE)

    def get_tag_from_soup(self, soup: BeautifulSoup, tag: str, class_name: str = None) -> list:
        if class_name is None:
            return soup.findAll(tag)
        else:
            return soup.findAll(tag, class_=class_name)

    def get_attributes_from_tag(self, tag: BeautifulSoup, *attributes) -> dict[str, str]:
        if len(attributes) == 0:
            return tag.attrs
        else:
            return {attribute: tag[attribute] for attribute in attributes}