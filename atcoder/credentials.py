from struction.credentials import AbstractCredentials
import requests.cookies

class AtCoderCredentials(AbstractCredentials):

    revel_session: str
    csrf_token: str

    def __init__(self, revel_session: str):
        self.revel_session = revel_session
        self.csrf_token = AtCoderCredentials.fetch_csrf_from_session(self.revel_session)

    def inject(self, session: requests.Session):
        session.cookies.set("REVEL_SESSION", self.revel_session)

    @staticmethod
    def extract(cookies: requests.cookies.RequestsCookieJar):
        data = cookies.get("REVEL_SESSION")
        if data is None:
            raise Exception("Failed to extract AtCoderCredentials from cookies")

        return AtCoderCredentials(data)

    def serialize(self):
        return {
            "revel_session": self.revel_session
        }

    @staticmethod
    def deserialize(data: dict):
        return AtCoderCredentials(
            data["revel_session"]
        )
