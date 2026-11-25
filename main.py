#!/usr/bin/env python3
"""One Emoji, One Dream Vacation -- make.fun entry.

Exactly one emoji for my dream vacation, kept in entry.txt
next to this file. This program reads those exact bytes, checks
them against the bounty gate rule by rule, and publishes them
byte for byte to /output/entry.txt.

The emoji: a desert island. No flight, no hotel, no itinerary,
no people -- just sand, one palm tree and the sea in every
direction. It is the most evocative single picture of a dream
vacation because it is the one every other vacation is trying
to be: nowhere to be, nobody to answer to, nothing on the
schedule but the tide. Candidates I considered and cut: a
sunset over the sea (beautiful, but a postcard, not a plan),
a mountain (a trip with effort in it -- the opposite of a
dream), and a cocktail (a drink is an evening, not a vacation).
The island won because it is the whole holiday in one glyph:
arrival, escape and nowhere else to go.

Gate (from the kit's RULES.txt): /output/entry.txt must be UTF-8
text of 1 to 8 characters, not only white space. The entry is
modelled as an Emoji: the decoded text plus the facts the gate
needs about it (its length in characters and in bytes, its one
code point, its Unicode name and category), and the gate is a
list of checks over that Emoji, so a failure names the rule
that refused the entry and the character that broke it. The
program also guards the silent corruption that would waste
the entry: a variation selector or invisible joiner smuggled
in beside the emoji, which would make it two characters.

Run it the way the grader does:

    python3 main.py
"""

import os
import sys
import unicodedata

ENTRY_FILE = "entry.txt"
OUT_PATH = "/output/entry.txt"
MIN_CHARS = 1
MAX_CHARS = 8


def is_emoji(char):
    """True when the character is an emoji: a symbol in the
    Unicode emoji ranges, not a letter, digit or punctuation."""
    code = ord(char)
    if unicodedata.category(char) == "So":
        return True
    return (0x1F300 <= code <= 0x1FAFF or 0x2600 <= code <= 0x27BF
            or 0x2B00 <= code <= 0x2BFF or 0xFE00 <= code <= 0xFE0F)


class Emoji:
    """The entry as a value: the decoded text plus the facts
    the gate needs about it, computed once."""

    def __init__(self, text, raw_bytes):
        self.text = text
        self.raw_bytes = raw_bytes
        self.length = len(text)
        self.codepoints = [ord(ch) for ch in text]
        self.names = [unicodedata.name(ch, "?") for ch in text]
        self.is_single_emoji = (
            self.length == 1 and is_emoji(text))

    def describe(self):
        names = ", ".join(self.names)
        return (f"entry={self.text!r} chars={self.length} "
                f"bytes={len(self.raw_bytes)} names=[{names}]")


def gate_checks(emoji):
    """Yield (rule, passed, detail) for every gate rule."""
    yield ("utf-8", True, "decoded as UTF-8")
    yield ("length", MIN_CHARS <= emoji.length <= MAX_CHARS,
           f"{emoji.length} characters (need {MIN_CHARS} to {MAX_CHARS})")
    yield ("one-character", emoji.length == 1,
           "exactly one character" if emoji.length == 1
           else f"{emoji.length} characters, not one")
    yield ("is-emoji", emoji.is_single_emoji,
           f"a single emoji ({emoji.names[0]})" if emoji.is_single_emoji
           else "not a single emoji")
    yield ("no-invisible", all(unicodedata.category(ch) != "Cf"
                                for ch in emoji.text),
           "no invisible joiner or variation selector")
    yield ("non-blank", bool(emoji.text.strip()),
           "more than white space")


def validate(emoji):
    """Fail on the first gate check that does not pass."""
    passed = []
    for name, ok, detail in gate_checks(emoji):
        if not ok:
            raise SystemExit(f"gate fail [{name}]: {detail} "
                             f"({emoji.describe()})")
        passed.append(f"{name}={detail}")
    print(f"gate: {'; '.join(passed)}", file=sys.stderr)


def read_entry_bytes():
    """Read entry.txt as raw bytes, exactly as committed."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, ENTRY_FILE), "rb") as fh:
        return fh.read()


def decode_entry(data):
    """Decode the entry bytes as UTF-8, refusing anything else."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"gate fail [utf-8]: {exc}") from exc


def verify_published(path, data):
    """Re-read what was written and refuse a byte mismatch."""
    with open(path, "rb") as fh:
        published = fh.read()
    if published != data:
        raise SystemExit("published entry does not match entry.txt")


def publish(data):
    """Write the bytes unchanged to /output/entry.txt, falling
    back to ./entry.txt, and verify the published bytes match."""
    try:
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "wb") as fh:
            fh.write(data)
        path = OUT_PATH
    except OSError:
        path = os.path.join(os.getcwd(), "entry.txt")
        with open(path, "wb") as fh:
            fh.write(data)
    verify_published(path, data)
    return path


def main():
    data = read_entry_bytes()
    emoji = Emoji(decode_entry(data), data)
    validate(emoji)
    path = publish(data)
    print(f"Wrote {emoji.length} characters to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
