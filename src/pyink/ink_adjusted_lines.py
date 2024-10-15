"""Module that provides the adjusted_lines used by incremental formatting.

This is separate from pyink.ink to make dependency management easier. And this
module will be folded to pyink.ink in the future.
"""

from collections.abc import Collection, Sequence
import dataclasses
import difflib


def is_valid_line_range(lines: tuple[int, int]) -> bool:
    """Returns whether the line range is valid."""
    return not lines or lines[0] <= lines[1]


def adjusted_lines(
    lines: Collection[tuple[int, int]],
    original_source: str,
    modified_source: str,
) -> list[tuple[int, int]]:
    """Returns the adjusted line ranges based on edits from the original code.

    This computes the new line ranges by diffing original_source and
    modified_source, and adjust each range based on how the range overlaps with
    the diffs.

    Note the diff can contain lines outside of the original line ranges. This can
    happen when the formatting has to be done in adjacent to maintain consistent
    local results. For example:

    1. def my_func(arg1, arg2,
    2.             arg3,):
    3.   pass

    If it restricts to line 2-2, it can't simply reformat line 2, it also has
    to reformat line 1:

    1. def my_func(
    2.     arg1,
    3.     arg2,
    4.     arg3,
    5. ):
    6.   pass

    In this case, we will expand the line ranges to also include the whole diff
    block.

    Args:
      lines: a collection of line ranges.
      original_source: the original source.
      modified_source: the modified source.
    """
    lines_mappings = _calculate_lines_mappings(original_source, modified_source)

    new_lines = []
    # Keep an index of the current search. Since the lines and lines_mappings are
    # sorted, this makes the search complexity linear.
    current_mapping_index = 0
    for start, end in sorted(lines):
        start_mapping_index = _find_lines_mapping_index(
            start,
            lines_mappings,
            current_mapping_index,
        )
        end_mapping_index = _find_lines_mapping_index(
            end,
            lines_mappings,
            start_mapping_index,
        )
        current_mapping_index = start_mapping_index
        if start_mapping_index >= len(lines_mappings) or end_mapping_index >= len(
            lines_mappings
        ):
            # Protect against invalid inputs.
            continue
        start_mapping = lines_mappings[start_mapping_index]
        end_mapping = lines_mappings[end_mapping_index]
        if start_mapping.is_changed_block:
            # When the line falls into a changed block, expands to the whole block.
            new_start = start_mapping.modified_start
        else:
            new_start = (
                start - start_mapping.original_start + start_mapping.modified_start
            )
        if end_mapping.is_changed_block:
            # When the line falls into a changed block, expands to the whole block.
            new_end = end_mapping.modified_end
        else:
            new_end = end - end_mapping.original_start + end_mapping.modified_start
        new_range = (new_start, new_end)
        if is_valid_line_range(new_range):
            new_lines.append(new_range)
    return new_lines


@dataclasses.dataclass
class _LinesMapping:
    """1-based lines mapping from original source to modified source.

    Lines [original_start, original_end] from original source
    are mapped to [modified_start, modified_end].

    The ranges are inclusive on both ends.
    """

    original_start: int
    original_end: int
    modified_start: int
    modified_end: int
    # Whether this range corresponds to a changed block, or an unchanged block.
    is_changed_block: bool


def _calculate_lines_mappings(
    original_source: str,
    modified_source: str,
) -> Sequence[_LinesMapping]:
    """Returns a sequence of _LinesMapping by diffing the sources.

    For example, given the following diff:
        import re
      - def func(arg1,
      -   arg2, arg3):
      + def func(arg1, arg2, arg3):
          pass
    It returns the following mappings:
      original -> modified
       (1, 1)  ->  (1, 1), is_changed_block=False (the "import re" line)
       (2, 3)  ->  (2, 2), is_changed_block=True (the diff)
       (4, 4)  ->  (3, 3), is_changed_block=False (the "pass" line)

    You can think this visually as if it brings up a side-by-side diff, and tries
    to map the line ranges from the left side to the right side:

      (1, 1)->(1, 1)    1. import re          1. import re
      (2, 3)->(2, 2)    2. def func(arg1,     2. def func(arg1, arg2, arg3):
                        3.   arg2, arg3):
      (4, 4)->(3, 3)    4.   pass             3.   pass

    Args:
      original_source: the original source.
      modified_source: the modified source.
    """
    matcher = difflib.SequenceMatcher(
        None,
        original_source.splitlines(keepends=True),
        modified_source.splitlines(keepends=True),
    )
    matching_blocks = matcher.get_matching_blocks()
    lines_mappings: list[_LinesMapping] = []
    # matching_blocks is a sequence of "same block of code ranges", see
    # https://docs.python.org/3/library/difflib.html#difflib.SequenceMatcher.get_matching_blocks
    # Each block corresponds to a _LinesMapping with is_changed_block=False,
    # and the ranges between two blocks corresponds to a _LinesMapping with
    # is_changed_block=True,
    # NOTE: matching_blocks is 0-based, but _LinesMapping is 1-based.
    for i, block in enumerate(matching_blocks):
        if i == 0:
            if block.a != 0 or block.b != 0:
                lines_mappings.append(
                    _LinesMapping(
                        1,
                        block.a,
                        1,
                        block.b,
                        False,
                    )
                )
        else:
            previous_block = matching_blocks[i - 1]
            lines_mappings.append(
                _LinesMapping(
                    previous_block.a + previous_block.size + 1,
                    block.a,
                    previous_block.b + previous_block.size + 1,
                    block.b,
                    True,
                )
            )
        if i < len(matching_blocks) - 1:
            lines_mappings.append(
                _LinesMapping(
                    block.a + 1,
                    block.a + block.size,
                    block.b + 1,
                    block.b + block.size,
                    False,
                )
            )
    return lines_mappings


def _find_lines_mapping_index(
    original_line: int,
    lines_mappings: Sequence[_LinesMapping],
    start_index: int,
) -> int:
    """Returns the original index of the lines mappings for the original line."""
    index = start_index
    while index < len(lines_mappings):
        mapping = lines_mappings[index]
        if (
            mapping.original_start <= original_line
            and original_line <= mapping.original_end
        ):
            return index
        index += 1
    return index
