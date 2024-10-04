from Constants import Constants


class CurrencyConvertor:
    def __init__(self, exchange_rates: dict[tuple[str, str], float] = Constants.EXCHANGE_RATES):
        # Define the exchange rates relative to MDL
        self.exchange_rates = exchange_rates

    def convert(self, price: float, from_currency: str, to_currency) -> float | None:
        try:
            suitable_exchange_rate = self.exchange_rates.get((from_currency, to_currency))
        except KeyError:
            return None
        return price * suitable_exchange_rate
