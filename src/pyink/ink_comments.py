"""Utilities related to comments.

This is separate from pyink.ink to avoid circular dependencies.
"""

import re

from pyink.mode import Mode


def comment_contains_pragma(comment: str, mode: Mode) -> bool:
    """Check if the given string contains one of the pragma forms.

    A pragma form can appear at the beginning of a comment:
      # pytype: disable=attribute-error
    or somewhere in the middle:
      # some comment # type: ignore # another comment
    or the comments can even be separated by a semicolon:
      # some comment; noqa: E111; another comment

    Args:
      comment: The comment to check.
      mode: The mode that defines which pragma forms to check for.

    Returns:
      True if the comment contains one of the pragma forms.
    """
    joined_pragma_expression = "|".join(mode.pyink_annotation_pragmas)
    pragma_regex = re.compile(rf"([#|;] ?(?:{joined_pragma_expression}))")
    return pragma_regex.search(comment) is not None
