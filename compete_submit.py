import glob
import json
import os
import re
import subprocess
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
    replace_current_line, CPP_FAKE_INCLUDE_PATH, make_progress
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


def fetch_gcc_includes() -> set:
    print("Fetching gcc includes...")
    proc = subprocess.run(["g++", "-print-file-name=include"], capture_output=True)

    find_dir = proc.stdout.decode().strip()

    replace_current_line("Fetched. include directory: " + os.path.abspath(find_dir) + "\n")

    includes = set()
    if not os.path.exists(find_dir):
        return includes
    if not os.path.isdir(find_dir):
        return includes
    for i in glob.glob(os.path.join(find_dir, "**/*"), recursive=True):
        if os.path.isdir(i):
            continue
        includes.add(os.path.relpath(i, find_dir))

    print(f"Detected {len(includes)} include files.")

    return includes


def expand_include_source(source_path: str, source: str):
    if not os.path.exists(CPP_FAKE_INCLUDE_PATH):
        includes = fetch_gcc_includes()
        total = len(includes)
        cur = 0
        sys.stdout.write("Creating fake source...")
        for i in includes:
            path = str(os.path.join(CPP_FAKE_INCLUDE_PATH, i))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            cur += 1
            replace_current_line("Creating fake source... " + make_progress(cur, total, 10) + f" {cur}/{total}")
            with open(path, 'a'):
                pass

        os.makedirs(os.path.join(CPP_FAKE_INCLUDE_PATH, "atcoder"), exist_ok=True)
        with open(os.path.join(CPP_FAKE_INCLUDE_PATH, "atcoder", "all"), 'a'):
            pass

        replace_current_line("Completed\n")

    original_includes = re.findall(r"#include\s+<.+>", source)
    original_includes.extend(re.findall(r'#include\s+"atcoder/all"', source))

    include_directories = [
        "",
        "c++",
        "c++/x86_64-w64-mingw32",  # これは環境により変化するかもしれない
        "c++/backward"
    ]

    cmds = ["g++", "-nostdinc++", "-x", "c++", "-isystem", source_path, "-D", "ONLINE_JUDGE", "-D", "ATCODER", "-E",
            "-CC", "-P", "-", "-o", "-"]

    for i in include_directories:
        cmds.extend(["-I", os.path.join(CPP_FAKE_INCLUDE_PATH, i)])

    proc = subprocess.run(cmds, input=source.encode(),
                          capture_output=True)

    if len(proc.stderr.decode().strip()) > 0:
        print_err(proc.stderr.decode())
        return False

    result = "\n".join(original_includes) + "\n" + proc.stdout.decode()

    return result


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

    if current_preferences.submit_delay > 0:
        for i in range(current_preferences.submit_delay, 0, -1):
            replace_current_line(make_ascii_escaped(f"Submitting in {i} seconds...", AsciiColors.BRIGHT_YELLOW))
            time.sleep(1)
        sys.stdout.write("\n")
    source = find_source()
    if source is None:
        return

    with open(source, 'r', encoding='utf-8') as f:
        content = f.read().replace("\r", "")

    with open(TESTCASES_CACHE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    matched = re.search(r"// compete BOF([\s\S]*)// compete EOF", content)
    if matched is None:
        formatted_content = content
    else:
        formatted_content = matched.group(1)

    if current_preferences.cpp_expand_include_files:
        formatted_content = expand_include_source(os.path.dirname(source), formatted_content)

        if not formatted_content:
            print_err("Failed to preprocess source. cancelled submission")
            return

    problem = Problem.deserialize(data)
    replace_current_line(make_ascii_escaped(f"Submitting {problem.problem_id}...", AsciiColors.BRIGHT_GREEN))
    sys.stdout.write("\r\n")
    handler = AtCoderSubmissionHandler(problem.problem_id)
    if handler.submit(formatted_content, AtCoderSubmissionOption()):
        compete_watch.run(True)
    else:
        if os.name == 'nt':
            print(make_ascii_escaped("Pasted to clipboard instead of submitting.", AsciiColors.YELLOW))
            subprocess.run(["clip"], input=formatted_content.encode("shift-jis"))


if __name__ == '__main__':
    run()
