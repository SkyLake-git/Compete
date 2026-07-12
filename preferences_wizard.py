import sys

from const import make_ascii_escaped, AsciiColors, make_ascii_move, clear_after_lines, print_err, clear_current_line
from struction.preferences import Preferences, PreferenceKeys, PREFERENCE_KEY_LIST
from aggregate import current_preferences, save_current_preferences


def wizard(keys: list[str], force: bool = False) -> bool:
    data = current_preferences.serialize()
    if force:
        force_suffix = ""
    else:
        force_suffix = " (optional)"
    for k in keys:
        if force:
            desc = ""
        else:
            desc = make_ascii_escaped("Leave blank and press ENTER to skip.", AsciiColors.BRIGHT_BLACK) + "\n"
        if PreferenceKeys.description(k) is not None:
            desc += PreferenceKeys.description(k)
        row = len(desc.split("\n"))

        while True:
            print(desc)
            value = input(make_ascii_escaped(f"Set preference \"{k}\"{force_suffix}: ", AsciiColors.BRIGHT_CYAN, AsciiColors.BRIGHT_BLACK))
            sys.stdout.write(make_ascii_move(row + 1))
            clear_after_lines()
            if len(value) == 0:
                if force:
                    print_err("Please input value")
                else:
                    print(make_ascii_escaped(f"Skipped ({k})", AsciiColors.BRIGHT_BLACK))
                    break
            else:
                value_set = PreferenceKeys.try_from(k, value)
                if value_set is None:
                    print_err(f"Failed to decode {value}. Please check value type in README.md")
                    continue
                print(make_ascii_escaped(f"Set preference ({k}) to {value_set}", AsciiColors.BRIGHT_YELLOW))
                data[k] = value_set
                break
    current_preferences.update(Preferences.deserialize(data))
    print(make_ascii_escaped("Successfully changed preferences", AsciiColors.BRIGHT_GREEN))
    save_current_preferences()


if __name__ == '__main__':
    wizard(PREFERENCE_KEY_LIST)