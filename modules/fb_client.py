import requests

class FBClient:
    def __init__(self, cookie: str):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile; rv:109.0) Gecko/110.0 Firefox/110.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": cookie
        })
        self.base = "https://mbasic.facebook.com"

    def get(self, url, **kwargs):
        if not url.startswith("http"):
            url = self.base + url
        return self.session.get(url, **kwargs)

    def post(self, url, data=None, **kwargs):
        if not url.startswith("http"):
            url = self.base + url
        return self.session.post(url, data=data, **kwargs)