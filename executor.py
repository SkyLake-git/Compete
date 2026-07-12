import glob
import os.path
import re
import subprocess
import time
import psutil
import sysconfig

from aggregate import *
from const import *

def format_testcase_string(v: str) -> str:
    return v.strip().replace(" ", "\n")

def split_partition(t: str) -> list[tuple[str, str]]:
    if len(t) <= 0:
        return []
    ret = []
    b1, s1, r1 = t.partition(" ")
    b2, s2, r2 = t.partition("\n")
    if len(b1) < len(b2):
        ret.append((b1, s1))
        ret.extend(split_partition(r1))
        return ret
    else:
        ret.append((b2, s2))
        ret.extend(split_partition(r2))
        return ret


def judge_stdout(stdout: str, testcase: Testcase) -> tuple[bool, list[tuple[str, str, str, bool]]]:
    expected_lines = split_partition(testcase.expected.strip())
    stdout_lines = stdout.strip().split()
    if len(expected_lines) != len(stdout_lines):
        return False, []
    judges = []

    failed = False
    for i in range(len(expected_lines)):
        e = expected_lines[i][0]
        o = stdout_lines[i]

        current = True
        if (re.match(r"[0-9]+\.[0-9]+", e) is not None) or (re.match(r"[0-9]+\.[0-9]+", o) is not None):  # float
            if abs(float(e) - float(o)) > 1E-6:
                current = False
                failed = True
        elif e != o:
            current = False
            failed = True

        judges.append((e, expected_lines[i][1], o, current))

    return not failed, judges

def execute(target: str, testcase: Testcase) -> RuntimeTestcase:
    proc = subprocess.Popen(target, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.stdin.write(testcase.inputs.encode())
    proc.stdin.flush()
    start = time.time()

    killed = False
    psproc = psutil.Process(proc.pid)
    last_cputime = None
    while proc.poll() is None:
        if psproc.is_running():
            try:

                v = psproc.cpu_times()
                last_cputime = v.user
            except psutil.NoSuchProcess:
                pass
        duration = max(last_cputime, time.time() - start)

        temp_result = waiting_judge_to_string()
        if duration >= testcase.time_limit:
            temp_result = testcase_result_to_string(TestcaseResult.TIME_LIMIT_EXCEEDED)

        replace_current_line(
            make_ascii_escaped(f"- {testcase.label} ", AsciiColors.DEFAULT,
                                      AsciiColors.BRIGHT_BLACK) + " " + temp_result + make_ascii_escaped(
                f" {round(duration * 1000)}ms",
                AsciiColors.BRIGHT_PURPLE))

        if duration > testcase.time_limit * 2:
            proc.kill()
            killed = True
            break

    duration = time.time() - start
    clear_current_line()
    stdout = proc.stdout.read().decode()
    stderr = proc.stderr.read().decode()

    additional_data = []
    judge_result, judges = judge_stdout(stdout, testcase)
    if proc.returncode != 0 and (not killed):
        judge = TestcaseResult.RUNTIME_ERROR
        additional_data.append(f"Return code: {proc.returncode}")
    elif duration >= testcase.time_limit:
        judge = TestcaseResult.TIME_LIMIT_EXCEEDED
    elif not judge_result:
        judge = TestcaseResult.WRONG_ANSWER
    else:
        judge = TestcaseResult.ACCEPTED

    if killed:
        additional_data.append("Process was terminated due to TLE")

    rt = RuntimeTestcase(testcase.label, testcase.inputs, testcase.expected, testcase.time_limit, judge, stdout,
                         stderr,
                         duration, last_cputime, judges)
    rt.additional_data = additional_data

    return rt

def find_executable_by_cmake(candidates: list):
    path = ROOT_PATH
    if not os.path.exists(os.path.join(path, "CMakeLists.txt")):
        return None

    with open(os.path.join(path, "CMakeLists.txt"), 'r', encoding='utf-8') as f:
        matched = re.search(r"project\((.*)\)", f.read())

    if matched is None:
        print_err("cannot find project name")
        return None

    project_name = matched.group(1)
    print(make_ascii_escaped(f"Detected project name: {project_name}", AsciiColors.BRIGHT_BLACK))
    pattern = os.path.join(path, "cmake-build-*", f"{project_name}.exe")

    candidates.extend(glob.glob(pattern, recursive=True))
    return None

def find_executable() -> typing.Union[str, None]:
    candidates = []
    if current_preferences.executable_path is not None:
        candidates.append(current_preferences.executable_path)

    find_executable_by_cmake(candidates)
    latest_target = None
    latest_modified_time = -1
    for file in candidates:
        print(make_ascii_escaped(f"Found executable: {os.path.abspath(file)}", AsciiColors.BRIGHT_BLACK))
        modified_time = os.path.getmtime(file)

        if modified_time > latest_modified_time:
            latest_target = file
            latest_modified_time = modified_time

    if latest_target is None:
        print_err("Couldn't find executables")
        return None

    return latest_target

def execute_testcases(target: str, testcases: list[Testcase]) -> list[RuntimeTestcase]:
    print(make_ascii_escaped(f"Executing {os.path.abspath(target)}", AsciiColors.BRIGHT_BLACK))

    results: list[RuntimeTestcase] = []
    ac_count = 0
    tx = []
    for t in testcases:
        r = execute(target, t)
        results.append(r)
        if r.result == TestcaseResult.ACCEPTED:
            ac_count += 1
        sys.stdout.write(make_ascii_progress(1, round((len(tx) / len(testcases)) * 100)))
        r.pretty_print()
        tx.append(testcase_result_to_string(r.result))
    print(f"\n({len(results)}/{len(testcases)}) ┃ " + "  ".join(tx) + " ┃")
    print(make_ascii_progress_reset())
    if ac_count == len(testcases):
        print(
            make_ascii_escaped("┃ \n┃ Fully accepted, Good job\n┃ ", AsciiColors.BRIGHT_GREEN))

    return results