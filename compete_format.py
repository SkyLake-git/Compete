import os
import sys
import time

import compete_submit
from const import make_ascii_escaped, print_err, AsciiColors

if __name__ == '__main__':
    path = sys.argv[1]

    if not path.endswith(".cpp"):
        print_err("Specified file type is unsupported, supported file types: .cpp")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    start = time.time()
    formatted = compete_submit.format_source_code(path, content)
    took = time.time() - start
    print("Took " + str(round(took * 1000, 1)) + "ms")
    if not formatted:
        print_err("Failed to format source.")
    else:
        if os.name == 'nt':
            compete_submit.clip(formatted)
            print(make_ascii_escaped("Pasted to clipboard.", AsciiColors.YELLOW))
        else:
            print(formatted)
