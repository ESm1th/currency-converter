import json
from datetime import datetime
from http.client import HTTPSConnection


class CurrencyConverter:

    """Convert requested amount from `USD` to `RUB` currency."""

    def __init__(self) -> None:
        self._rate = self.get_convertion_rate()

    def update(self) -> None:
        self._rate = self.get_convertion_rate()

    def get_convertion_rate(self) -> dict:
        """
        Send request to free API to get exchange rates from `USD` to all
        other currencies and then return dict with exchange rate for
        only russian `RUB`, `USD` as `base` key currency and timestamp
        for caching purposes.
        """
        connection = HTTPSConnection('api.exchangerate-api.com')
        connection.request('GET', '/v4/latest/USD')
        response = connection.getresponse()
        data = json.loads(response.read())
        return {
            'base': data['base'],  # USD
            'timestamp': datetime.utcnow(),  # for caching purposes
            'rate': data['rates']['RUB']
        }

    def convert(self, amount: float) -> dict:
        """Returns dict with data about requested conversation."""
        return {
            'from': self._rate['base'],
            'amount': amount,
            'to': 'RUB',
            'result': amount * self._rate['rate']
        }

    def check_rate(self) -> bool:
        """
        Checking timedelta for utcnow() and `self._rate` timestamp attribute.
        If this value is equal or greater then 18000 seconds - return `False`,
        otherwise return True.
        """
        delta = datetime.utcnow() - self._rate['timestamp']
        if delta.seconds >= 18000:
            return False
        return True
