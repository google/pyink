"""Utilities related to comments.

This is separate from pyink.ink to avoid circular dependencies.
"""

import re

from blib2to3 import pytree
from blib2to3.pgen2 import token
from pyink import mode as mode_mod


def comment_contains_pragma(comment: str, mode: mode_mod.Mode) -> bool:
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


def is_skip_target_safe(leaf: pytree.Leaf) -> bool:
  """Returns True if the node ignored by `# fmt: skip` is safe to hide."""
  prev_sibling = leaf.prev_sibling
  parent = leaf.parent
  if not prev_sibling and parent:
    # If the immediate sibling is missing, we climb to the parent's sibling to
    # locate the semantic statement target (e.g., when the comment is at the
    # end of a docstring block).
    prev_sibling = parent.prev_sibling
  return (
      isinstance(prev_sibling, pytree.Leaf)
      and prev_sibling.type == token.STRING
  )
