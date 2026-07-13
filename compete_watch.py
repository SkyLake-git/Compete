import json
import sys
import time

from atcoder.submission import AtCoderSubmissionHandler, pretty_print_submissions
from const import TESTCASES_CACHE_PATH, Problem, make_ascii_move, clear_after_lines, TestcaseResult


def run(auto_exit: bool):
    with open(TESTCASES_CACHE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    problem = Problem.deserialize(data)

    handler = AtCoderSubmissionHandler(problem.problem_id)
    repeated = False
    while True:
        submissions = handler.fetch_submissions(10)
        should_exit = True
        for s in submissions:
            if s.result == TestcaseResult.WAITING_JUDGE:
                should_exit = False
                break
        if repeated:
            clear_after_lines()
        print()
        pretty_print_submissions(submissions)
        if auto_exit:
            break
        if should_exit:
            time.sleep(6)
        else:
            time.sleep(4)
        repeated = True
        sys.stdout.write(make_ascii_move(len(submissions) + 1))


if __name__ == '__main__':
    run(False)
