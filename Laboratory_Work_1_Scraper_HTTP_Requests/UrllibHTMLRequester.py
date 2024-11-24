from urllib.request import Request, urlopen
from Laboratory_Work_1_Scraper_HTTP_Requests.Constants import Constants
from Laboratory_Work_1_Scraper_HTTP_Requests.WebScraper import WebScraper


class UrllibHTMLRequester(WebScraper):
    def __init__(self):
        super().__init__()

    def create_request(self, custom_url: str = Constants.URL_WEBSITE, custom_headers: dict = Constants.HEADERS) -> Request:
        return Request(
            url=custom_url,
            headers=custom_headers
        )

    # POINT 2 - GET REQUEST TO DARWIN PHONES PAGE
    def get_html_from_url(self, request: Request = None) -> str:
        # POINT 2 - GET REQUEST TO DARWIN PHONES PAGE
        if request is None:
            request = self.create_request()

        page = urlopen(request)
        html_bytes = page.read()
        return html_bytes.decode(Constants.DECODE_FORMAT)
