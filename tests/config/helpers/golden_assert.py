from pathlib import Path
import difflib


def normalize(text: str) -> list[str]:
    return [line.rstrip() for line in text.strip().splitlines()]


def diff_strings(expected: str, actual: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            normalize(expected),
            normalize(actual),
            fromfile="expected",
            tofile="actual",
            lineterm=""
        )
    )


def assert_golden(path: Path, actual: str, update: bool = False):

    if update:
        path.write_text(actual)
        return

    expected = path.read_text()

    if normalize(expected) != normalize(actual):
        diff = diff_strings(expected, actual)

        raise AssertionError(
            f"\n\n❌ GOLDEN MISMATCH: {path.name}\n\n{diff}\n"
        )