import datetime
import os.path
import re
import subprocess
import sys
import time

import requests
from bs4 import BeautifulSoup
from aggregate import current_credentials, current_preferences
from atcoder.constants import *
from const import ContestType, print_err, LIB_PATH, make_ascii_escaped, AsciiColors, replace_current_line, \
    clear_current_line, TestcaseResult, make_progress, testcase_result_to_string, fill_space
from requests_wrapper import get_requests, RequestsWrapper
from struction.submission import SubmissionHandler, Submission, SubmissionOption, SubmissionResult

class AtCoderSubmissionResult(SubmissionResult):
    progress_current: int
    progress_max: int
    result: int

    def __init__(self, progress_current, progress_max, result):
        self.progress_current = progress_current
        self.progress_max = progress_max
        self.result = result

    def is_accepted(self):
        return self.result == TestcaseResult.ACCEPTED

    def to_string(self):
        if self.progress_max > -1:
            suffix = f"{self.progress_current}/{self.progress_max} " + make_progress(self.progress_current, self.progress_max, 10) + " "
            res = fill_space(testcase_result_to_string(self.result), 21)
        else:
            suffix = ""
            res = testcase_result_to_string(self.result)


        return res + suffix

class AtCoderSubmissionOption(SubmissionOption):
    pass

class AtCoderSubmission(Submission):
    result: AtCoderSubmissionResult

    def __init__(self, created: int, problem: str, time_consumption: float, result: AtCoderSubmissionResult, memory_consumption: float):
        self.created = created
        self.problem = problem
        self.time_consumption = time_consumption
        self.result = result
        self.memory_consumption = memory_consumption

    def get_time_consumption_string(self):
        if self.time_consumption > 0:
            return str(round(self.time_consumption * 1000)) + " ms"
        else:
            return ""

    def get_memory_consumption_string(self):
        if self.memory_consumption > 0:
            return str(round(self.memory_consumption)) + " KiB"
        else:
            return ""

class AtCoderSubmissionHandler(SubmissionHandler):
    prob: str
    wrapper: RequestsWrapper

    def __init__(self, prob):
        self.prob = prob
        self.wrapper = get_requests(ContestType.ATCODER)

    def submit(self, content: str, option: AtCoderSubmissionOption) -> bool:
        url = get_submission_url(self.prob)
        if current_preferences.language_id is None:
            print_err("Failed to submit: Preference \"language_id\" is not set")
            raise Exception("Failed to submit")

        post_res = self.wrapper.post(url, {
            "csrf_token": current_credentials.atcoder.csrf_token,
            "data.TaskScreenName": self.prob,
            "data.LanguageId": to_language_id(current_preferences.language_id),
            "sourceCode": content,
        }, allow_redirects=True)
        post_res.raise_for_status()

        if post_res.status_code != 302:
            replace_current_line(make_ascii_escaped("Failed to submit, make sure you're participating in a contest", AsciiColors.BRIGHT_RED))
        else:
            replace_current_line(make_ascii_escaped("Successfully submitted", AsciiColors.BRIGHT_GREEN))
        sys.stdout.write("\n")

        return post_res.status_code == 302

    def can_fetch_submissions(self) -> bool:
        return True

    def fetch_submissions(self) -> list[AtCoderSubmission]:
        res = self.wrapper.get(get_my_submissions_url(self.prob))
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        submissions = []
        table = soup.find("table")
        if table is None:
            return []
        for d in table.find("tbody").find_all("tr"):
            datum = d.find_all("td", limit=9)

            parsed_progress_result = re.search("([0-9]+)/([0-9]+)", datum[6].text)
            parsed_result = re.search("([A-Z]+)", datum[6].text)
            if parsed_result is None:
                print_err("Failed to detect result from: " + datum[6].text)
                result = TestcaseResult.WAITING_JUDGE
            else:
                result = TestcaseResult.from_string(parsed_result.group(1))

            if parsed_progress_result is None:
                progress_current = -1
                progress_max = -1
            else:
                progress_current = int(parsed_progress_result.group(1))
                progress_max = int(parsed_progress_result.group(2))

            if result != TestcaseResult.COMPILE_ERROR:
                parsed_time_consumption = re.search("([0-9]+) ms", datum[7].text)
                if parsed_time_consumption is None:
                    print_err("Failed to detect time consumption from: " + datum[7].text)
                    time_consumption = -1
                else:
                    time_consumption = float(parsed_time_consumption.group(1)) / 1000

                parsed_memory_consumption = re.search("([0-9]+) KiB", datum[8].text)
                if parsed_memory_consumption is None:
                    print_err("Failed to detect memory consumption from: " + datum[8].text)
                    memory_consumption = -1
                else:
                    memory_consumption = float(parsed_memory_consumption.group(1))
            else:
                time_consumption = -1
                memory_consumption = -1

            submissions.append(AtCoderSubmission(
                int(datetime.datetime.strptime(datum[0].text, "%Y-%m-%d %H:%M:%S%z").timestamp()),
                datum[1].text,
                time_consumption,
                AtCoderSubmissionResult(
                    progress_current,
                    progress_max,
                    result
                ),
                memory_consumption
            ))

        return submissions

def pretty_print_submissions(l: list[AtCoderSubmission]):
    max_sizes = []
    contents = []
    for submission in l:
        c = [
            datetime.datetime.fromtimestamp(submission.created).strftime("%Y-%m-%d %H:%M:%S"),
            submission.problem,
            submission.get_time_consumption_string(),
            submission.get_memory_consumption_string(),
            submission.result.to_string()
        ]
        for i in range(len(c)):
            if len(max_sizes) <= i:
                max_sizes.append(len(c[i]))
                continue
            if max_sizes[i] < len(c[i]):
                max_sizes[i] = len(c[i])
        contents.append(c)

    for c in contents:
        sys.stdout.write("┃ ")
        cp = []
        for i in range(len(c)):
            cp.append(fill_space(c[i], max_sizes[i]))
        sys.stdout.write(" ┃ ".join(cp))
        sys.stdout.write(" ┃\n")
