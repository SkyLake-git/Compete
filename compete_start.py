import json
from html.parser import HTMLParser
import re
from requests_wrapper import *
import const
from atcoder.constants import *


class TestcasesParser(HTMLParser):
    io_div_depth: int
    div_depth: int
    part_count: int
    part_seq: int
    testcase_seq: int  # 0 -> waiting input, 1 -> waiting output
    time_limit: float
    current: const.Testcase
    testcases: list[const.Testcase]
    wait_data: bool
    wait_time_limit: bool
    time_limit_seq: int
    ended: bool

    def __init__(self):
        super().__init__()
        self.io_div_depth = -1
        self.div_depth = 0
        self.part_count = 0
        self.part_seq = -1
        self.testcase_seq = -1
        self.time_limit = -1
        self.current = const.Testcase("", "", "", self.time_limit)
        self.wait_data = False
        self.wait_time_limit = False
        self.time_limit_seq = -1
        self.ended = False
        self.testcases = []

    def handle_starttag(self, tag, attrs):
        if self.ended: return
        if tag == "div":
            self.div_depth += 1

        if self.time_limit_seq == 0 and tag == "p":
            self.wait_time_limit = True

        if self.time_limit_seq == -1 and tag == "div":
            for k, v in attrs:
                if k == "class" and v == "col-sm-12":  # input
                    self.time_limit_seq = 0
                    break

        if self.io_div_depth == -1 and tag == "div":
            for k, v in attrs:
                if k == "class" and v == "io-style":  # input
                    self.io_div_depth = self.div_depth
                    break
        else:
            for k, v in attrs:
                if self.part_seq >= 0 and k == "class" and v == "part":
                    self.part_count += 1
                if k == "class" and v == "lang-en":
                    self.finalize()
                    return

        if self.part_seq >= 0 and self.testcase_seq == -1 and tag == "pre":
            self.testcase_seq = 0

        if self.testcase_seq >= 0 and tag == "pre" and self.part_count > 0:
            self.part_count -= 1
            self.wait_data = True

    def finalize(self):
        self.io_div_depth = -1
        self.part_seq = -1
        if self.testcase_seq != 0:
            raise Exception("Unexpected testcase sequence (expected 0): " + str(self.testcase_seq))
        self.testcase_seq = -1
        self.ended = True

    def handle_data(self, data):
        if self.ended: return
        if self.wait_time_limit:
            matched = re.search("([1-9|.]+) sec", data)
            if matched is None:
                raise Exception("Failed to parse time limit: " + data)

            self.time_limit = float(matched.group(1))
        if self.wait_data:
            if self.testcase_seq == 0:
                self.current.inputs = data

            if self.testcase_seq == 1:
                if self.time_limit == -1:
                    raise Exception("Time limit is still unparsed")
                self.current.expected = data
                self.current.time_limit = self.time_limit
                self.current.label = "Sample " + str(len(self.testcases) + 1)
                self.testcases.append(self.current)
                self.current = const.Testcase("", "", "", self.time_limit)

    def handle_endtag(self, tag):
        if self.ended: return
        if tag == "div":
            self.div_depth -= 1

            if self.div_depth < self.io_div_depth:
                self.part_seq = 0

            if self.div_depth < self.io_div_depth - 1:
                self.finalize()

        if tag == "p" and self.time_limit_seq >= 0:
            self.wait_time_limit = False
            self.time_limit_seq = 1

        if tag == "pre" and self.testcase_seq >= 0 and self.wait_data:
            self.testcase_seq += 1
            self.wait_data = False

            if self.testcase_seq >= 2:
                self.testcase_seq = 0

def run():
    if len(sys.argv) <= 1:
        target_prob = input(const.make_ascii_escaped("AtCoder Problem ID: ", const.AsciiColors.BRIGHT_CYAN,
                                                     const.AsciiColors.BRIGHT_BLACK))
    else:
        target_prob = sys.argv[1]

    wrapper = get_requests(ContestType.ATCODER)

    res = wrapper.get(get_problem_url(target_prob))
    if res.status_code != 200:
        print("request failed")
        exit(2)

    parser = TestcasesParser()
    parser.feed(res.text)

    problem = Problem(target_prob, parser.testcases)
    for t in parser.testcases:
        t.pretty_print()

    with open(const.TESTCASES_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(problem.serialize(), f)

    print(const.make_ascii_escaped(f"Scraped {len(parser.testcases)} test cases", const.AsciiColors.BRIGHT_GREEN))
    print(const.make_ascii_escaped(f"Compete {target_prob} started, Good luck", const.AsciiColors.BRIGHT_CYAN,
                                   const.AsciiColors.BRIGHT_BLACK))

if __name__ == '__main__':
    run()