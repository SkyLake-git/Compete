import json
import os
import typing
from atcoder.credentials import AtCoderCredentials
from struction.preferences import Preferences
from const import CREDENTIALS_PATH, PREFERENCES_PATH


class CredentialsStore:
    atcoder: typing.Union[None, AtCoderCredentials]

    def __init__(self, atcoder: typing.Union[None, AtCoderCredentials]):
        self.atcoder = atcoder

    def serialize(self):
        data = {}

        if self.atcoder is not None:
            data["atcoder"] = self.atcoder.serialize()
        else:
            data["atcoder"] = None

        return data

    @staticmethod
    def deserialize(data: dict):
        if data["atcoder"] is not None:
            atcoder = AtCoderCredentials.deserialize(data["atcoder"])
        else:
            atcoder = None

        return CredentialsStore(atcoder)

DEFAULT_CREDENTIALS = CredentialsStore(None)
current_credentials: CredentialsStore = DEFAULT_CREDENTIALS

if os.path.exists(CREDENTIALS_PATH):
    with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
        current_credentials = CredentialsStore.deserialize(json.load(f))

def save_current_credentials():
    with open(CREDENTIALS_PATH, 'w', encoding='utf-8') as fp:
        json.dump(current_credentials.serialize(), fp, indent=4)

save_current_credentials()

DEFAULT_PREFERENCES = Preferences()
current_preferences: Preferences = DEFAULT_PREFERENCES

if os.path.exists(PREFERENCES_PATH):
    with open(PREFERENCES_PATH, 'r', encoding='utf-8') as f:
        current_preferences = Preferences.deserialize(json.load(f))

def save_current_preferences():
    with open(PREFERENCES_PATH, 'w', encoding='utf-8') as fp:
        json.dump(current_preferences.serialize(), fp, indent=4)

save_current_preferences()