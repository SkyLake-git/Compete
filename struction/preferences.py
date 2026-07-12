import typing
from const import *
from languages import SourceLanguages, NAME_MAPPINGS


class PreferenceKeys:
    EXECUTABLE_PATH = "executable_path"
    SOURCE_PATH = "source_path"
    LANGUAGE_ID = "language_id"
    REQUEST_DBG_REMAIN_TAIL = "request_dbg_remain_tail"

    @staticmethod
    def description(k: str):
        if k == PreferenceKeys.EXECUTABLE_PATH:
            return "Executable file path (e.g. \"a.exe\")"
        elif k == PreferenceKeys.SOURCE_PATH:
            return "Source code file path (e.g. \"a.cpp\")"
        elif k == PreferenceKeys.LANGUAGE_ID:
            l = []
            for k, v in NAME_MAPPINGS.items():
                l.append(f"{v}: {k}")

            return "\n".join(l)
        return None

    @staticmethod
    def try_from(k: str, v: str):
        try:
            if k == PreferenceKeys.EXECUTABLE_PATH or k == PreferenceKeys.SOURCE_PATH:
                return v
            elif k == PreferenceKeys.LANGUAGE_ID:
                return int(v)
            else:
                return (v.lower() == "true") or (v.lower() == "yes")
        except ValueError:
            return None

PREFERENCE_KEY_LIST = [PreferenceKeys.EXECUTABLE_PATH, PreferenceKeys.SOURCE_PATH, PreferenceKeys.LANGUAGE_ID, PreferenceKeys.REQUEST_DBG_REMAIN_TAIL]

class Preferences:
    executable_path: typing.Union[None, str]
    source_path: typing.Union[None, str]
    language_id: typing.Union[None, int]
    request_dbg_remain_tail: bool

    def __init__(
            self,
            executable_path: typing.Union[None, str] = None,
            source_path: typing.Union[None, str] = None,
            language_id: typing.Union[None, int] = None,
            request_dbg_remain_tail: bool = True
    ):
        self.executable_path = executable_path
        self.source_path = source_path
        self.language_id = language_id
        self.request_dbg_remain_tail = request_dbg_remain_tail

        if executable_path is not None:
            if not os.path.exists(executable_path):
                raise Exception("Specified executable path does not exists: " + executable_path)
            if os.path.splitext(executable_path)[1] != ".exe":
                raise Exception("Specified executable path is not executable: " + executable_path)

        if source_path is not None:
            if not os.path.exists(source_path):
                raise Exception("Specified source path does not exists: " + executable_path)

    def serialize(self):
        return {
            PreferenceKeys.EXECUTABLE_PATH: self.executable_path,
            PreferenceKeys.SOURCE_PATH: self.source_path,
            PreferenceKeys.LANGUAGE_ID: self.language_id,
            PreferenceKeys.REQUEST_DBG_REMAIN_TAIL: self.request_dbg_remain_tail
        }

    def update(self, another):
        self.executable_path = another.executable_path
        self.source_path = another.source_path
        self.language_id = another.language_id
        self.request_dbg_remain_tail = another.request_dbg_remain_tail

    @staticmethod
    def deserialize(data: dict):
        return Preferences(
            dict_getdefault(data, PreferenceKeys.EXECUTABLE_PATH),
            dict_getdefault(data, PreferenceKeys.SOURCE_PATH),
            dict_getdefault(data, PreferenceKeys.LANGUAGE_ID),
            dict_getdefault(data, PreferenceKeys.REQUEST_DBG_REMAIN_TAIL, True)
        )