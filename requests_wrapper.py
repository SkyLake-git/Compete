import requests as internal_requests
import typing
from const import *
from struction.credentials import AbstractCredentials
from aggregate import current_credentials, current_preferences

class RequestMethodPrefixes:

    @staticmethod
    def get():
        return make_ascii_escaped(" GET ", AsciiColors.BRIGHT_CYAN)

    @staticmethod
    def post():
        return make_ascii_escaped(" POST ", AsciiColors.BRIGHT_GREEN)


class RequestsWrapper:

    session: internal_requests.Session

    def __init__(self, session):
        self.session = session
        self.always_tail = True

    @staticmethod
    def response_to_text(code: int):
        if 100 <= code <= 199:
            color = AsciiColors.CYAN
        elif code <= 299:
            color = AsciiColors.BRIGHT_GREEN
        elif code <= 399:
            color = AsciiColors.BRIGHT_PURPLE
        elif code <= 499:
            color = AsciiColors.BRIGHT_RED
        elif code <= 599:
            color = AsciiColors.BRIGHT_RED
        else:
            color = AsciiColors.BRIGHT_BLACK

        return make_ascii_escaped(str(code), color)

    @staticmethod
    def start_request_dbg(url, method_prefix):
        sys.stdout.write("  " + method_prefix + url + "\r")

    @staticmethod
    def end_request_dbg(url, method_prefix, code, code_ok):
        if code_ok and (not current_preferences.request_dbg_remain_tail):
            clear_current_line()
            sys.stdout.write("\r")
        else:
            replace_current_line("  " + RequestsWrapper.response_to_text(code) + method_prefix + url)
            sys.stdout.write("\r\n")

    def get(self, url, **kwargs) -> internal_requests.Response:
        RequestsWrapper.start_request_dbg(url, RequestMethodPrefixes.get())
        res = self.session.get(url, **kwargs)
        RequestsWrapper.end_request_dbg(url, RequestMethodPrefixes.get(), res.status_code, 99 < res.status_code <= 399)
        return res

    def post(self, url, data=None, **kwargs) -> internal_requests.Response:
        RequestsWrapper.start_request_dbg(url, RequestMethodPrefixes.post())
        res = self.session.post(url, data, **kwargs)
        RequestsWrapper.end_request_dbg(url, RequestMethodPrefixes.post(), res.status_code, 99 < res.status_code <= 399)
        return res

def make_request_wrapper(cred: typing.Union[None,  AbstractCredentials] = None) -> RequestsWrapper:
    session = internal_requests.Session()
    session.headers = REQUEST_HEADERS
    if cred is not None:
        cred.inject(session)

    return RequestsWrapper(session)

_REQUEST_WRAPPERS = {
    ContestType.ATCODER: make_request_wrapper(current_credentials.atcoder)
}

def get_requests(ctype: int) -> RequestsWrapper:
    if not ctype in _REQUEST_WRAPPERS:
        raise Exception(f"Wrapper for contest type \"{ctype}\" is not defined")

    return _REQUEST_WRAPPERS[ctype]