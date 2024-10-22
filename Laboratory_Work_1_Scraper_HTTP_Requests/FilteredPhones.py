class FilteredPhones:
    def __init__(self, filtered_phones: list, sum_prices: float, utc_timestamp: float):
        self.filtered_phones = filtered_phones
        self.sum_prices = sum_prices
        self.utc_timestamp = utc_timestamp

    def __repr__(self):
        phone_entities_repr = ', '.join([repr(phone_entity) for phone_entity in self.filtered_phones])
        return f"FilteredPhones([{phone_entities_repr}], {self.sum_prices}, {self.utc_timestamp})"
