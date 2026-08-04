import glob
import os.path
import re
import subprocess
import time
from typing import Any, IO

import preferences_wizard
from aggregate import current_preferences
from const import print_err, make_ascii_escaped, AsciiColors
from struction.preferences import PreferenceKeys


def extract_score(io: IO[Any]) -> int:
    res = io.read().decode()
    matched = re.search(r"Score = ([0-9]+)", res)
    if matched is None:
        print_err("Couldn't detect score from tester: " + res)
        raise RuntimeError()

    return int(matched.group(1))


def create(inp: str) -> subprocess.Popen:
    assert current_preferences.heuristic_tester_path is not None
    assert current_preferences.heuristic_executable_path is not None

    cmd = [
        current_preferences.heuristic_tester_path,
        current_preferences.heuristic_executable_path,
        "<",
        inp,
        ">",
        "nul"
    ]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
    return proc


def test(inputs: list[str]):
    processes: list[subprocess.Popen] = []

    scores: list[int] = []
    poll_index = 0
    index = 0
    total = 0
    while poll_index < len(inputs):
        if poll_index >= len(processes) - 7 and index < len(inputs):
            processes.append(create(inputs[index]))
            index += 1
            continue
        if processes[poll_index].poll() is None:
            time.sleep(0.01)
            continue
        stderr = processes[poll_index].stderr
        assert stderr is not None

        score = extract_score(stderr)
        total += score
        scores.append(score)
        print(make_ascii_escaped(f"Case #{str(poll_index + 1)}:", AsciiColors.DEFAULT,
                                 AsciiColors.BRIGHT_BLACK) + " " + str(score))
        poll_index += 1

    print(f"\nTotal Score: {total}")


def main():
    if current_preferences.heuristic_executable_path is None:
        preferences_wizard.wizard([PreferenceKeys.HEURISTIC_EXECUTABLE_PATH], True)
        assert current_preferences.heuristic_executable_path is not None
    if current_preferences.heuristic_tester_path is None:
        preferences_wizard.wizard([PreferenceKeys.HEURISTIC_TESTER_PATH], True)
        assert current_preferences.heuristic_tester_path is not None

    if current_preferences.heuristic_testcase_dir_path is None:
        preferences_wizard.wizard([PreferenceKeys.HEURISTIC_TESTCASE_DIR_PATH], True)
        assert current_preferences.heuristic_testcase_dir_path is not None

    params = []

    for file in glob.glob(os.path.join(current_preferences.heuristic_testcase_dir_path, "*.txt")):
        with open(file, 'r', encoding='utf-8') as f:
            params.append(file)

    test(params)


if __name__ == '__main__':
    main()
