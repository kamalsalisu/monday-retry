import requests
import json
from urllib.parse import quote


class MixpanelMiddleware:
    def __init__(self, token):
        self.mixpanel_token = token

    def send_to_mixpanel(self, event_type, event_data):
        url = "https://api.mixpanel.com/track#live-event"
        headers = {
            "Accept": "text/plain",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        event_data["token"] = self.mixpanel_token
        event_data["distinct_id"] = 'apps@makrwatch.com'
        data = {
            "event": event_type,
            "properties": event_data
        }
        j = json.dumps(data)
        query = quote(j.encode('utf-8'))
        payload = "data={}&verbose=1&ip=1".format(query)
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)
