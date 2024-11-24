from Laboratory_Work_1_Scraper_HTTP_Requests.Constants import Constants
from Laboratory_Work_1_Scraper_HTTP_Requests.Phone import Price


def construct_price_currency(price: float, currency: str) -> Price:
    price_obj = Price(price=price, currency=currency)
    return price_obj


class CurrencyConvertor:
    def __init__(self, exchange_rates: dict[tuple[str, str], float] = Constants.EXCHANGE_RATES):
        self.exchange_rates = exchange_rates

    def convert(self, price: float, from_currency: str, to_currency) -> float | None:
        try:
            suitable_exchange_rate = self.exchange_rates.get((from_currency, to_currency))
        except KeyError:
            if from_currency == to_currency:
                return price
            return None
        return price * suitable_exchange_rate

    def get_currencies(self) -> list[str]:
        return list(set([currency for currency_tuple in self.exchange_rates.keys() for currency in currency_tuple]))