import json

import executor
from const import *

def run() -> list[RuntimeTestcase]:
    with open(TESTCASES_CACHE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    problem = Problem.deserialize(data)

    target = executor.find_executable()
    if target is None:
        return []
    return executor.execute_testcases(target, problem.testcases)


if __name__ == '__main__':
    run()