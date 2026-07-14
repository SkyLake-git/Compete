import sys

import compete_start
import compete_submit
import compete_test
import compete_watch
import credentials_wizard
import preferences_wizard

from const import *
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_err("Please specify argument [1]: command")
        exit(1)

    cmd = sys.argv[1]
    sys.argv.pop(1)

    if cmd == "start":
        compete_start.run()
    elif cmd == "test":
        compete_test.run()
    elif cmd == "credentials" or cmd == "cred":
        credentials_wizard.run()
    elif cmd == "submit":
        compete_submit.run()
    elif cmd == "watch":
        compete_watch.run(False)
    elif cmd == "preferences" or cmd == "pref":
        preferences_wizard.run()
    else:
        print_err("Unknown command: " + cmd)