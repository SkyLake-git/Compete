import re
import urllib.parse
from abc import abstractmethod

import requests.cookies

class AbstractCredentials:
    @staticmethod
    def fetch_csrf_from_session(revel_session: str) -> str:
        revel_session = urllib.parse.unquote(revel_session)
        matched = re.search(r"csrf_token:(([0-9a-zA-Z]|\+|/|=)+)", revel_session)
        if matched is None:
            raise RuntimeError("Couldn't detect \"csrf_token\"")

        return matched.group(1)

    @abstractmethod
    def inject(self, session: requests.Session):
        pass

    @staticmethod
    @abstractmethod
    def extract(cookies: requests.cookies.RequestsCookieJar):
        pass

