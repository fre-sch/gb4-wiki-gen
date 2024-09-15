import requests
from urllib.parse import urljoin


class ApiSession(requests.Session):
    def __init__(self, base_url=None):
        super().__init__()
        self.base_url = base_url

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)

    # additional api methods

    def login_token(self):
        """
        Example response object
            {
                "batchcomplete": "",
                "query": {
                    "tokens": {
                        "logintoken": "4fea3540e34bfa1c73cca295c040ba9066e555c9+\\"
                    }
                }
            }
        """
        querystring = {
            "action": "query",
            "format": "json",
            "meta": "tokens",
            "type": "login",
        }
        response = self.get(
            "api.php",
            params=querystring,
        )
        response.raise_for_status()
        response_data = response.json()
        return response_data["query"]["tokens"]["logintoken"]

    def bot_login(self, username, password):
        login_token = self.login_token()
        request_data = {
            "action": "login",
            "format": "json",
            "lgtoken": login_token,
            "lgname": username,
            "lgpassword": password,
        }
        response = self.post(
            "api.php",
            data=request_data
        )
        response.raise_for_status()
        # bot login sends set-cookie headers, which the session captures
        # the response contains no relevant credentials
        return True

    def csrf_token(self):
        """
        Example Response Object
            {
            "batchcomplete": "",
            "query": {
                "tokens": {
                "csrftoken": "d0ea519e37af4ae9d05944633fcb366c66e5579b+\\"
                }
            }
            }
        """
        request_data = {
            "action": "query",
            "format": "json",
            "meta": "tokens"
        }
        response = self.get("api.php", params=request_data)
        response.raise_for_status()
        response_data = response.json()
        return response_data["query"]["csrftoken"]
