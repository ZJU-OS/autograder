import re

from .utils import color

__all__ = ["assert_equal", "assert_lines_match"]


def assert_equal(got, expect, msg: str = ""):
    if got == expect:
        return
    if msg:
        msg += "\n"
    raise AssertionError(
        f"{msg}got:\n  {str(got).replace(chr(10), chr(10) + '  ')}\n"
        f"expected:\n  {str(expect).replace(chr(10), chr(10) + '  ')}"
    )


def assert_lines_match(text: str, *regexps: str, **kw):
    def assert_lines_match_kw(no=None):
        return no or []

    no = assert_lines_match_kw(**kw)

    # Check text against regexps
    lines = text.splitlines()
    good = set()
    bad = set()
    remaining_regexps = list(regexps)

    for i, line in enumerate(lines):
        # Check for required patterns
        for regexp in remaining_regexps[:]:  # Copy list to avoid modification during iteration
            if re.search(regexp, line):
                good.add(i)
                remaining_regexps.remove(regexp)
                break

        # Check for forbidden patterns
        if any(re.search(r, line) for r in no):
            bad.add(i)

    if not remaining_regexps and not bad:
        return

    # We failed; construct an informative failure message
    show = set()
    for lineno in good.union(bad):
        for offset in range(-2, 3):
            show.add(lineno + offset)
    if remaining_regexps:
        show.update(n for n in range(len(lines) - 5, len(lines)))

    msg = []
    last = -1
    for lineno in sorted(show):
        if 0 <= lineno < len(lines):
            if lineno != last + 1:
                msg.append("...")
            last = lineno
            line_marker = (
                color("red", "BAD ") if lineno in bad else color("green", "GOOD") if lineno in good else "    "
            )
            msg.append(f"{line_marker} {lines[lineno]}")

    if last != len(lines) - 1:
        msg.append("...")
    if bad:
        msg.append("unexpected lines in output")
    for r in remaining_regexps:
        msg.append(color("red", "MISSING") + f" '{r}'")

    raise AssertionError("\n".join(msg))
