import json
import os
import re
import sys
import time
import typing

import compete_test
import compete_watch
import credentials_wizard
import preferences_wizard
from aggregate import current_preferences, current_credentials
from atcoder.submission import AtCoderSubmissionHandler, AtCoderSubmissionOption
from const import TestcaseResult, ROOT_PATH, print_err, make_ascii_escaped, AsciiColors, TESTCASES_CACHE_PATH, Problem, \
    replace_current_line
from struction.preferences import PreferenceKeys


def find_source_by_cmake(candidates: list):
    path = ROOT_PATH
    if not os.path.exists(os.path.join(path, "CMakeLists.txt")):
        return None

    with open(os.path.join(path, "CMakeLists.txt"), 'r', encoding='utf-8') as f:
        matched = re.search(r"add_executable\((.*) (.*)\)", f.read())

    if matched is None:
        print_err("cannot find project executable source")
        return None

    name = matched.group(2)
    print(make_ascii_escaped(f"Detected project executable source: {name}", AsciiColors.BRIGHT_BLACK))
    target = os.path.join(path, name)
    if os.path.exists(target):
        candidates.append(target)

    return None


def find_source() -> typing.Union[str, None]:
    candidates = []
    if current_preferences.source_path is not None:
        candidates.append(current_preferences.source_path)

    find_source_by_cmake(candidates)
    latest_target = None
    latest_modified_time = -1
    for file in candidates:
        print(make_ascii_escaped(f"Found executable source: {os.path.abspath(file)}", AsciiColors.BRIGHT_BLACK))
        modified_time = os.path.getmtime(file)

        if modified_time > latest_modified_time:
            latest_target = file
            latest_modified_time = modified_time

    if latest_target is None:
        print_err("Couldn't find executable sources")
        return None

    return latest_target


def run():
    if current_credentials.atcoder is None:
        print(make_ascii_escaped("Necessary credentials for AtCoder doesn't found.", AsciiColors.BRIGHT_YELLOW))
        print(make_ascii_escaped("Starting credentials wizard", AsciiColors.BRIGHT_YELLOW))
        credentials_wizard.wizard_atcoder()
    if current_preferences.language_id is None:
        print(make_ascii_escaped("Necessary preferences doesn't set.", AsciiColors.BRIGHT_YELLOW))
        print(make_ascii_escaped("Starting preferences wizard", AsciiColors.BRIGHT_YELLOW))
        preferences_wizard.wizard([PreferenceKeys.LANGUAGE_ID], True)
        preferences_wizard.wizard([PreferenceKeys.SOURCE_PATH], False)
    results = compete_test.run()

    ac = True
    for r in results:
        if r.result != TestcaseResult.ACCEPTED:
            ac = False
            break

    if not ac:
        return
    sys.stdout.write("\n")

    for i in range(2, 0, -1):
        replace_current_line(make_ascii_escaped(f"Submitting in {i} seconds...", AsciiColors.BRIGHT_YELLOW))
        time.sleep(1)
    sys.stdout.write("\n")
    source = find_source()
    if source is None:
        return

    with open(source, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(TESTCASES_CACHE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    problem = Problem.deserialize(data)

    replace_current_line(make_ascii_escaped(f"Submitting {problem.problem_id}...", AsciiColors.BRIGHT_GREEN))
    sys.stdout.write("\r\n")
    handler = AtCoderSubmissionHandler(problem.problem_id)
    if handler.submit(content, AtCoderSubmissionOption()):
        compete_watch.run(True)


if __name__ == '__main__':
    run()
