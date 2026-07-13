import math
import os
import shutil
import sys
from math import remainder

BASE_URL = "https://atcoder.jp/"
REQUEST_HEADERS = {
    'Accept-Language': 'ja',
    'User-Agent': 'zMozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36'
}

ROOT_PATH = os.path.join(os.path.dirname(__file__), "..")
LIB_PATH = os.path.dirname(__file__)
RESOURCES_PATH = os.path.join(LIB_PATH, "resources")
os.makedirs(RESOURCES_PATH, exist_ok=True)
TESTCASES_CACHE_PATH = os.path.join(RESOURCES_PATH, "testcases.json")
PREFERENCES_PATH = os.path.join(RESOURCES_PATH, "preferences.json")
CREDENTIALS_PATH = os.path.join(RESOURCES_PATH, "credentials.json")


class ContestType:
    ATCODER = 0


class TestcaseResult:
    ACCEPTED = 0
    WRONG_ANSWER = 1
    TIME_LIMIT_EXCEEDED = 2
    MEMORY_LIMIT_EXCEEDED = 3
    RUNTIME_ERROR = 4
    COMPILE_ERROR = 5
    WAITING_JUDGE = 6

    @staticmethod
    def from_string(s: str):
        if s == "AC":
            return TestcaseResult.ACCEPTED
        elif s == "WA":
            return TestcaseResult.WRONG_ANSWER
        elif s == "TLE":
            return TestcaseResult.TIME_LIMIT_EXCEEDED
        elif s == "MLE":
            return TestcaseResult.MEMORY_LIMIT_EXCEEDED
        elif s == "RE":
            return TestcaseResult.RUNTIME_ERROR
        elif s == "CE":
            return TestcaseResult.COMPILE_ERROR
        elif s == "WJ":
            return TestcaseResult.WAITING_JUDGE

        raise Exception("unknown testcase result: " + s)


class AsciiColors:
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    CYAN = 36
    WHITE = 37
    DEFAULT = 39
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_PURPLE = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97


def testcase_result_color(result: int) -> int:
    if result == TestcaseResult.ACCEPTED:
        return AsciiColors.BRIGHT_GREEN
    else:
        return AsciiColors.BRIGHT_YELLOW


def print_err(message: str):
    print(make_ascii_escaped("┃ " + message, AsciiColors.BRIGHT_RED))


def waiting_judge_to_string() -> str:
    return make_ascii_escaped(" WJ ", AsciiColors.BRIGHT_BLACK, AsciiColors.DEFAULT, code=7)


def testcase_result_to_string(result: int) -> str:
    if result == TestcaseResult.ACCEPTED:
        return make_ascii_escaped(" AC ", AsciiColors.BRIGHT_GREEN, AsciiColors.DEFAULT, code=7)
    elif result == TestcaseResult.WRONG_ANSWER:
        return make_ascii_escaped(" WA ", AsciiColors.BRIGHT_YELLOW, AsciiColors.DEFAULT, code=7)
    elif result == TestcaseResult.TIME_LIMIT_EXCEEDED:
        return make_ascii_escaped(" TLE ", AsciiColors.BRIGHT_YELLOW, AsciiColors.DEFAULT, code=7)
    elif result == TestcaseResult.MEMORY_LIMIT_EXCEEDED:
        return make_ascii_escaped(" MLE ", AsciiColors.BRIGHT_YELLOW, AsciiColors.DEFAULT, code=7)
    elif result == TestcaseResult.RUNTIME_ERROR:
        return make_ascii_escaped(" RE ", AsciiColors.BRIGHT_YELLOW, AsciiColors.DEFAULT, code=7)
    elif result == TestcaseResult.COMPILE_ERROR:
        return make_ascii_escaped(" CE ", AsciiColors.BRIGHT_YELLOW, AsciiColors.DEFAULT, code=7)
    elif result == TestcaseResult.WAITING_JUDGE:
        return waiting_judge_to_string()

    raise Exception("unknown result")


class Testcase:
    label: str
    inputs: str
    expected: str
    time_limit: float  # in seconds

    def __init__(self, label, inputs, expected, time_limit):
        self.label = label
        self.inputs = inputs
        self.expected = expected
        self.time_limit = time_limit

    def pretty_print(self):
        print("\n".join([
            make_ascii_escaped(f"- {self.label} ", AsciiColors.DEFAULT, AsciiColors.BRIGHT_BLACK),
            make_ascii_escaped("IN:", AsciiColors.BRIGHT_BLUE),
            self.inputs.strip(),
            make_ascii_escaped("EXPECTED:", AsciiColors.BRIGHT_PURPLE),
            self.expected.strip(),
            ""
        ]))

    def serialize(self):
        return {
            "label": self.label,
            "inputs": self.inputs.replace("\r", ""),
            "expected": self.expected.replace("\r", ""),
            "time_limit": self.time_limit
        }

    @staticmethod
    def deserialize(d):
        return Testcase(d["label"], d["inputs"], d["expected"], d["time_limit"])


class RuntimeTestcase(Testcase):
    result: int
    outputs: str
    err_outputs: str
    duration: float
    cpu_duration: float
    additional_data: list
    judges: list[tuple[str, str, bool]]

    def __init__(self, label, inputs, expected, time_limit, result, outputs, err_outputs, duration, cpu_duration,
                 judges):
        super().__init__(label, inputs, expected, time_limit)
        self.result = result
        self.outputs = outputs
        self.err_outputs = err_outputs
        self.duration = duration
        self.cpu_duration = cpu_duration
        self.judges = judges
        self.additional_data = []

    def pretty_print(self):
        if len(self.additional_data) >= 1:
            additional = "(" + ", ".join(self.additional_data) + ")"
        else:
            additional = ""

        if len(self.judges) >= 1:
            expected = ""
            actual = ""
            for e, sep, o, res in self.judges:
                if res:
                    color = AsciiColors.BRIGHT_GREEN
                else:
                    color = AsciiColors.BRIGHT_RED

                expected += make_ascii_escaped(e, color) + sep
                actual += make_ascii_escaped(o, color) + sep
        else:
            expected = self.expected.strip()
            actual = self.outputs.strip()
        c = [
            make_ascii_escaped(f"- {self.label} ", AsciiColors.DEFAULT,
                               AsciiColors.BRIGHT_BLACK) + " " + testcase_result_to_string(
                self.result) + make_ascii_escaped(
                f" real: {round(self.duration * 1000, 1)}ms, cpu: {round(self.cpu_duration * 1000, 1)}ms ",
                AsciiColors.BRIGHT_CYAN) + make_ascii_escaped(
                f"/{round(self.time_limit * 1000)}ms ", AsciiColors.BRIGHT_BLACK) + additional,
            make_ascii_escaped("IN:", AsciiColors.BRIGHT_BLUE),
            self.inputs.strip(),
            make_ascii_escaped("EXPECTED:", AsciiColors.BRIGHT_PURPLE),
            expected,
            make_ascii_escaped("ACTUAL:", AsciiColors.BRIGHT_PURPLE),
            actual.rstrip()
        ]

        if len(self.err_outputs.strip()) > 0:
            c.extend(
                [
                    make_ascii_escaped("ERR:", AsciiColors.BRIGHT_RED),
                    self.err_outputs
                ]
            )

        print("\n".join(c))


class Problem:
    problem_id: str
    testcases: list[Testcase]

    def __init__(self, problem_id: str, testcases: list[Testcase]):
        self.problem_id = problem_id
        self.testcases = testcases

    def serialize(self):
        return {
            "problem_id": self.problem_id,
            "testcases": [i.serialize() for i in self.testcases]
        }

    @staticmethod
    def deserialize(data):
        return Problem(
            data["problem_id"],
            list(map(Testcase.deserialize, data["testcases"]))
        )


def url_join(a, *b):
    return a + "/".join(b)


def make_ascii_escaped(v: str, text_color: int, bg_color: int = AsciiColors.DEFAULT, resets: bool = True,
                       code: int = 0):
    bg_color += 10  # bg offset
    b = f"\x1b[{code};{text_color};{bg_color}m" + v
    if resets:
        b += make_ascii_reset()
    return b


def make_ascii_progress(status: int, percentage: int):
    return f"\x1b]9;4;{status};{percentage}\x07"


def make_ascii_progress_reset():
    return f"\x1b]9;4;0;0\x07"


def make_ascii_bell():
    return f"\x07"


def make_ascii_move(row: int):
    if row > 0:
        suf = "F"
    else:
        suf = "E"
    return f"\x1b[{abs(row)}{suf}"


def block_wrap():
    sys.stdout.write(f"\x1b[?7h")


def allow_wrap():
    sys.stdout.write(f"\x1b[?7l")


def make_ascii_reset():
    return "\x1b[0m"


def dict_getdefault(t: dict, k, default=None):
    if k in t:
        return t[k]
    else:
        return default


def clear_current_line():
    sys.stdout.write(f"\r\x1b[2K")


def clear_after_lines():
    sys.stdout.write(f"\r\x1b[0J")


def replace_current_line(message: str):
    sys.stdout.write(f"\r\x1b[2K{message}\x1b[0K")


def make_progress(pcur, pmax, col):
    count = int(math.floor((pcur / pmax) / (1 / col)))
    rem = (pcur / pmax) - count * (1 / col)

    codes = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
    base = "█" * count
    base += codes[round((rem / (1 / col)) * 7)]
    base += " " * max(0, col - count - 1)

    return base


def fill_space(s, smax):
    s += max(0, smax - len(s)) * " "
    return s
