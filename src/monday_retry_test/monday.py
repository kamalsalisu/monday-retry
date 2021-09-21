import re
import requests
from requests import Timeout
from retry import retry_api_request


class Monday:
    def __init__(self, api_key):
        self.api_url = 'https://api.monday.com/v2/'
        self.api_key = api_key

    def _get_authorization_header(self):
        return {"Authorization": self.api_key}

    @retry_api_request
    def make_monday_call_with_retry(self, query=None, timeout=10, retry_count=2):
        try:
            response = requests.post(
                self.api_url, timeout=timeout, json={"query": query}, headers=self._get_authorization_header()
            ).json()
        except Timeout:
            return {'errors': 'Request timed out', 'delay': 0}
        if 'errors' not in response:
            return response
        else:
            return {'errors': response, 'delay': self._extract_delay_from_api_response(response['errors'])}

    @staticmethod
    def _extract_delay_from_api_response(errors):
        delay = 0
        for error in errors:
            if 'budget exhausted' in error['message']:
                message = error['message']
                f = re.search(r"(\d+ seconds)", message)
                try:
                    delay = int(f[0].split(' ')[0])
                except IndexError:
                    pass
        return delay
