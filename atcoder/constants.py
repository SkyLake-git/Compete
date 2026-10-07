from const import url_join
from languages import SourceLanguages
from urllib.parse import urlparse

BASE_URL = "https://atcoder.jp/"

SOURCE_LANGUAGE_MAPPINGS = {
    SourceLanguages.CPP_GCC: 6017,
    SourceLanguages.CPP_CLANG: 6116
}


def split_problem(prob: str) -> tuple[str, str]:
    a = prob.split("_")
    if len(a) != 2:
        raise Exception("prob is invalid (expected: xx_yy): " + prob)

    return a[0], prob


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_problem_url(prob):
    if is_valid_url(prob):
        return prob
    cont, task = split_problem(prob)
    return url_join(BASE_URL, "contests", cont, "tasks", task)


def get_submission_url(prob):
    cont, _ = split_problem(prob)
    return url_join(BASE_URL, "contests", cont, "submit")


def get_my_submissions_url(prob):
    cont, _ = split_problem(prob)
    return url_join(BASE_URL, "contests", cont, "submissions", "me")


def to_language_id(lang: int):
    if not lang in SOURCE_LANGUAGE_MAPPINGS:
        raise Exception("unknown language: " + str(lang))

    return SOURCE_LANGUAGE_MAPPINGS[lang]
