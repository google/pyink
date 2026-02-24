from collections.abc import Iterator
from dataclasses import replace
from typing import Any
from unittest.mock import patch

import pytest

import pyink
from pyink.mode import TargetVersion
from tests.util import (
    all_data_cases,
    assert_format,
    dump_to_stderr,
    read_data,
    read_data_with_mode,
)


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("pyink.dump_to_file", dump_to_stderr):
        yield


def check_file(subdir: str, filename: str, *, data: bool = True) -> None:
    args, source, expected = read_data_with_mode(subdir, filename, data=data)
    assert_format(
        source,
        expected,
        args.mode,
        fast=args.fast,
        minimum_version=args.minimum_version,
        lines=args.lines,
        no_preview_line_length_1=args.no_preview_line_length_1,
    )
    if args.minimum_version is not None:
        major, minor = args.minimum_version
        target_version = TargetVersion[f"PY{major}{minor}"]
        mode = replace(args.mode, target_versions={target_version})
        assert_format(
            source,
            expected,
            mode,
            fast=args.fast,
            minimum_version=args.minimum_version,
            lines=args.lines,
            no_preview_line_length_1=args.no_preview_line_length_1,
        )


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
@pytest.mark.parametrize("filename", all_data_cases("cases"))
def test_simple_format(filename: str) -> None:
    check_file("cases", filename)


@pytest.mark.parametrize("filename", all_data_cases("line_ranges_formatted"))
def test_line_ranges_line_by_line(filename: str) -> None:
    args, source, expected = read_data_with_mode("line_ranges_formatted", filename)
    assert (
        source == expected
    ), "Test cases in line_ranges_formatted must already be formatted."
    line_count = len(source.splitlines())
    for line in range(1, line_count + 1):
        assert_format(
            source,
            expected,
            args.mode,
            fast=args.fast,
            minimum_version=args.minimum_version,
            lines=[(line, line)],
        )


# =============== #
# Unusual cases
# =============== #


def test_empty() -> None:
    source = expected = ""
    assert_format(source, expected)


def test_patma_invalid() -> None:
  source, expected = read_data("miscellaneous", "pattern_matching_invalid")
  mode = pyink.Mode(target_versions={pyink.TargetVersion.PY310})
  with pytest.raises(pyink.parsing.InvalidInput) as exc_info:
    assert_format(source, expected, mode, minimum_version=(3, 10))

  exc_info.match(
      "Cannot parse for target version Python 3.10: 10:11:     case a := b:"
  )


def test_range_formatting_preserves_newlines() -> None:
  # Source: Class docstring followed by another class (2 empty lines)
  # The docstring is unformatted (long line) to trigger change
  source = (
      'class A:\n    """Updates the Candidate\'s Phased Release to the desired'
      " state. Args: rapid_candidate_id: The Rapid Candidate"
      ' ID."""\n\n\n\nclass'
      " PhasedReleaseClientFactory(metaclass=abc.ABCMeta):\n    pass\n"
  )

  # Expected: Formatted docstring + 3 empty lines
  expected = (
      "class A:\n"
      '    """Updates the Candidate\'s Phased Release to the desired state.\n'
      "\n"
      "    Args:\n"
      "      rapid_candidate_id: The Rapid Candidate ID.\n"
      '    """\n'
      "\n"
      "\n"
      "\n"
      "class PhasedReleaseClientFactory(metaclass=abc.ABCMeta):\n"
      "    pass\n"
  )

  # Range covering the unformatted docstring (line 2)
  lines = [(2, 2)]

  # assert_format(source, expected, lines=lines)

  # Debugging: Monkeypatch EmptyLineTracker._maybe_empty_lines
  from pyink.lines import EmptyLineTracker, Line

  original_maybe_empty_lines = EmptyLineTracker._maybe_empty_lines

  def debug_maybe_empty_lines(self, current_line: Line) -> tuple[int, int]:
    before, after = original_maybe_empty_lines(self, current_line)
    print(f"DEBUG: Line: {str(current_line).strip()!r}")
    print(
        "DEBUG:   Type:"
        f" {current_line.leaves[0].type if current_line.leaves else 'None'}"
    )
    print(f"DEBUG:   Is Comment: {current_line.is_comment}")
    print(f"DEBUG:   Is Class: {current_line.is_class}")
    print(f"DEBUG:   Depth: {current_line.depth}")
    print(
        "DEBUG:   Prefix:"
        f" {current_line.leaves[0].prefix if current_line.leaves else 'None'!r}"
    )
    print(
        "DEBUG:   Prefix newlines:"
        f" {current_line.leaves[0].prefix.count('\\n') if current_line.leaves else 0}"
    )
    print(f"DEBUG:   Calculated before: {before}, after: {after}")
    return before, after

  with patch.object(
      EmptyLineTracker,
      "_maybe_empty_lines",
      side_effect=debug_maybe_empty_lines,
      autospec=True,
  ):
    assert_format(source, "EXPECT_FAILURE", lines=lines)
