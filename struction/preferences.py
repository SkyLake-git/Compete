import typing
from const import *
from languages import SourceLanguages, NAME_MAPPINGS


class PreferenceKeys:
    EXECUTABLE_PATH = "executable_path"
    SOURCE_PATH = "source_path"
    LANGUAGE_ID = "language_id"
    REQUEST_DBG_REMAIN_TAIL = "request_dbg_remain_tail"
    SUBMIT_DELAY = "submit_delay"

    HEURISTIC_EXECUTABLE_PATH = "heuristic_executable_path"
    HEURISTIC_TESTER_PATH = "heuristic_tester_path"
    HEURISTIC_TESTCASE_DIR_PATH = "heuristic_testcase_dir_path"

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
            if k == PreferenceKeys.EXECUTABLE_PATH or k == PreferenceKeys.SOURCE_PATH or PreferenceKeys.HEURISTIC_TESTER_PATH or PreferenceKeys.HEURISTIC_TESTCASE_DIR_PATH or PreferenceKeys.HEURISTIC_EXECUTABLE_PATH:
                return v
            elif k == PreferenceKeys.LANGUAGE_ID or k == PreferenceKeys.SUBMIT_DELAY:
                return int(v)
            else:
                return (v.lower() == "true") or (v.lower() == "yes")
        except ValueError:
            return None

PREFERENCE_KEY_LIST = [
    PreferenceKeys.EXECUTABLE_PATH,
    PreferenceKeys.SOURCE_PATH,
    PreferenceKeys.LANGUAGE_ID,
    PreferenceKeys.REQUEST_DBG_REMAIN_TAIL,
    PreferenceKeys.SUBMIT_DELAY
]

class Preferences:
    executable_path: typing.Union[None, str]
    source_path: typing.Union[None, str]
    language_id: typing.Union[None, int]
    request_dbg_remain_tail: bool
    submit_delay: int

    heuristic_executable_path: typing.Union[None, str]
    heuristic_tester_path: typing.Union[None, str]
    heuristic_testcase_dir_path: typing.Union[None, str]

    def __init__(
            self,
            executable_path: typing.Union[None, str] = None,
            source_path: typing.Union[None, str] = None,
            language_id: typing.Union[None, int] = None,
            request_dbg_remain_tail: bool = True,
            submit_delay: int = 2,
            heuristic_executable_path: typing.Union[None, str] = None,
            heuristic_tester_path: typing.Union[None, str] = None,
            heuristic_testcase_dir_path: typing.Union[None, str] = None
    ):
        self.executable_path = executable_path
        self.source_path = source_path
        self.language_id = language_id
        self.request_dbg_remain_tail = request_dbg_remain_tail
        self.submit_delay = submit_delay
        self.heuristic_executable_path = heuristic_executable_path
        self.heuristic_tester_path = heuristic_tester_path
        self.heuristic_testcase_dir_path = heuristic_testcase_dir_path

        if executable_path is not None:
            if not os.path.exists(executable_path):
                raise Exception("Specified executable path does not exists: " + executable_path)
            if os.path.splitext(executable_path)[1] != ".exe":
                raise Exception("Specified executable path is not executable: " + executable_path)

        if source_path is not None:
            if not os.path.exists(source_path):
                raise Exception("Specified source path does not exists: " + source_path)

        if heuristic_tester_path is not None:
            if not os.path.exists(heuristic_tester_path):
                raise Exception("Specified heuristic tester path does not exists: " + heuristic_tester_path)

        if heuristic_testcase_dir_path is not None:
            if not os.path.exists(heuristic_testcase_dir_path):
                raise Exception("Specified heuristic testcase dir path does not exists: " + heuristic_testcase_dir_path)

    def serialize(self):
        return {
            PreferenceKeys.EXECUTABLE_PATH: self.executable_path,
            PreferenceKeys.SOURCE_PATH: self.source_path,
            PreferenceKeys.LANGUAGE_ID: self.language_id,
            PreferenceKeys.REQUEST_DBG_REMAIN_TAIL: self.request_dbg_remain_tail,
            PreferenceKeys.SUBMIT_DELAY: self.submit_delay,
            PreferenceKeys.HEURISTIC_EXECUTABLE_PATH: self.heuristic_executable_path,
            PreferenceKeys.HEURISTIC_TESTER_PATH: self.heuristic_tester_path,
            PreferenceKeys.HEURISTIC_TESTCASE_DIR_PATH: self.heuristic_testcase_dir_path
        }

    def update(self, another):
        self.executable_path = another.executable_path
        self.source_path = another.source_path
        self.language_id = another.language_id
        self.request_dbg_remain_tail = another.request_dbg_remain_tail
        self.submit_delay = another.submit_delay
        self.heuristic_executable_path = another.heuristic_executable_path
        self.heuristic_tester_path = another.heuristic_tester_path
        self.heuristic_testcase_dir_path = another.heuristic_testcase_dir_path

    @staticmethod
    def deserialize(data: dict):
        return Preferences(
            dict_getdefault(data, PreferenceKeys.EXECUTABLE_PATH),
            dict_getdefault(data, PreferenceKeys.SOURCE_PATH),
            dict_getdefault(data, PreferenceKeys.LANGUAGE_ID),
            dict_getdefault(data, PreferenceKeys.REQUEST_DBG_REMAIN_TAIL, True),
            dict_getdefault(data, PreferenceKeys.SUBMIT_DELAY, 2),
            dict_getdefault(data, PreferenceKeys.HEURISTIC_EXECUTABLE_PATH),
            dict_getdefault(data, PreferenceKeys.HEURISTIC_TESTER_PATH),
            dict_getdefault(data, PreferenceKeys.HEURISTIC_TESTCASE_DIR_PATH)
        )