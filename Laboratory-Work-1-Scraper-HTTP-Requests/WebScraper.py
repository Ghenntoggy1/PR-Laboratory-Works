# Web Scraper class
import json
from abc import abstractmethod, ABC

import requests
from Constants import Constants
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup


class WebScraper(ABC):
    def __init__(self):
        self.url = Constants.URL_WEBSITE

    @abstractmethod
    def create_request(self, custom_url: str, custom_headers):
        pass

    @abstractmethod
    def get_html_from_url(self, request = None) -> str:
        pass

    # POINT 3 - USE OF BEAUTIFULSOUP TO PARSE HTML CONTENT
    def get_soup_from_html(self, html: str) -> BeautifulSoup:
        print(html)
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