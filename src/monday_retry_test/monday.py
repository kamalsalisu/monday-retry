import re
from typing import Optional

import requests
from requests import Timeout

from .mixpanel_middleware import MixpanelMiddleware
from .retry import retry_api_request


class Monday:
    def __init__(self, api_key):
        self.api_url = 'https://api.monday.com/v2/'
        self.api_key = api_key
        self.mixpanel_middleware: Optional[MixpanelMiddleware] = None

    def _get_authorization_header(self):
        return {"Authorization": self.api_key}

    def initiate_track_with_mixpanel(self, mixpanel_token):
        self.mixpanel_middleware = MixpanelMiddleware(mixpanel_token)

    @retry_api_request
    def make_monday_call_with_retry(self, query=None, timeout=10, retry_count=2):
        try:
            response = requests.post(
                self.api_url, timeout=timeout, json={"query": query}, headers=self._get_authorization_header()
            ).json()
        except Timeout:
            self._mixpanel_logger('Timeout')
            return {'errors': 'Request timed out', 'delay': 0}
        if 'errors' not in response:
            return response
        else:
            self._mixpanel_logger('Complexity')
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

    def _mixpanel_logger(self, error_type: str):
        if self.mixpanel_middleware:
            try:
                self.mixpanel_middleware.send_to_mixpanel("Monday API Error", {"Monday Error Type": error_type})
            except Exception:
                pass
