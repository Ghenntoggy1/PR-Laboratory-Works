# Web Scraper class
import json
from abc import abstractmethod, ABC
from typing import Union

import requests
from Laboratory_Work_1_Scraper_HTTP_Requests.Constants import Constants
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup, PageElement


class WebScraper(ABC):
    def __init__(self):
        self.url = Constants.URL_WEBSITE

    @abstractmethod
    def create_request(self, custom_url: str, custom_headers: dict):
        pass

    @abstractmethod
    def get_html_from_url(self, request=None) -> str:
        pass

    # POINT 3 - USE OF BEAUTIFULSOUP TO PARSE HTML CONTENT
    def get_soup_from_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, Constants.PARSER_TYPE)

    def get_tag_from_soup(self, soup: BeautifulSoup, tag: str, class_name: str = None) -> Union[list, PageElement]:
        if class_name is None:
            return soup.findAll(tag)
        else:
            return soup.findAll(tag, class_=class_name)

    def get_attributes_from_tag(self, tag: BeautifulSoup, attributes: list, keys: list = None) -> dict:
        if len(attributes) == 0:
            return tag.attrs
        else:
            formed_dict = {}
            for key in keys:
                formed_dict[key] = tag[attributes[keys.index(key)]]
            index = len(keys)
            for i in range(index, len(attributes)):
                key_value = attributes[i]
                formed_dict[key_value] = tag[key_value]
            return formed_dict
            # if key is not None:
            #     return {key: tag[attribute] for attribute in attributes}
            # else:
            #     return {attribute: tag[attribute] for attribute in attributes}
