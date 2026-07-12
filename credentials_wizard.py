import time

from requests_wrapper import *
from atcoder.credentials import AtCoderCredentials
from aggregate import save_current_credentials

def validate_atcoder(cred: AbstractCredentials) -> bool:
    wrapper = make_request_wrapper(cred)
    res = wrapper.get(url_join(BASE_URL, "settings"))
    if "login" in res.url:
        print_err("AtCoder credentials validation failed: Failed to open user settings")
        return False

    return True

def wizard_atcoder() -> None:
    while True:
        sys.stdout.flush()
        print("To get AtCoder credentials, see README.md")
        revel_session_raw = input(make_ascii_escaped("REVEL_SESSION: ", AsciiColors.BRIGHT_CYAN, AsciiColors.BRIGHT_BLACK))
        sys.stdout.write(make_ascii_move(1))
        clear_after_lines()
        try:
            csrf_token = AtCoderCredentials.fetch_csrf_from_session(revel_session_raw)
        except RuntimeError:
            print_err("Failed to detect csrf_token")
            continue

        print(make_ascii_escaped("Detected csrf_token: " + csrf_token, AsciiColors.BRIGHT_BLACK))

        cred = AtCoderCredentials(revel_session_raw)

        if not validate_atcoder(cred):
            continue


        break

    current_credentials.atcoder = cred
    save_current_credentials()

    print(make_ascii_escaped("Successfully registered.", AsciiColors.BRIGHT_GREEN))


def run():
    ctype_raw = input(
        make_ascii_escaped("Choose competition site to register credentials (a/atcoder): ", AsciiColors.BRIGHT_CYAN,
                           AsciiColors.BRIGHT_BLACK)).lower()

    mappings = {
        "a": ContestType.ATCODER,
        "atcoder": ContestType.ATCODER
    }

    if not ctype_raw in mappings:
        print_err("Unknown competition site: " + ctype_raw)
        exit(1)

    ctype = mappings[ctype_raw]

    if ctype == ContestType.ATCODER:
        wizard_atcoder()

if __name__ == '__main__':
    run()