"""Module that contains Pyink specific additions to line range formatting.

This is a separate module for easier patch management.
"""

from blib2to3 import pygram
from pyink import nodes as nodes_mod


def expand_lines_for_incompatible_formatting(
    src_node: nodes_mod.Node, lines_set: set[int]
) -> set[int]:
  """Expand lines_set to format more lines.

  The implementation of some formatting rules is very messy and some rules are
  so incompatible with line range formatting that it would require a large
  refactoring to properly support them. Therefore, this is Pyink's patch to
  detect problematic cases and solve them by formatting more lines.

  Args:
    src_node: The source node to expand the lines set for.
    lines_set: The initial set of chosen line indices.

  Returns:
    Indices of new lines to which formatting should be applied as well.
  """
  if not lines_set:
    return set()
  return _expand_lines_set_for_leading_comments(src_node, lines_set)


def _expand_lines_set_for_leading_comments(
    src_node: nodes_mod.Node, lines_set: set[int]
) -> set[int]:
  """Expands lines_set to include the first line of a top-level class/def.

  Example:
  ```
  import foo  # <- line range only on this line


  # Comment about Bar
  class Bar():
    pass
  ```
  We extend the formatting from the import line to the Bar class.

  Args:
    src_node: The source node to expand the lines set for.
    lines_set: The initial set of chosen line indices.

  Returns:
    Indices of new lines to which formatting should be applied as well.
  """
  added_lines = set()
  prev_is_import = False
  prev_import_in_lines_set = False
  for child in src_node.children:
    first = nodes_mod.first_leaf(child)
    if first is None:
      continue
    prefix_lines = _get_prefix_line_range(first)

    if (
        _is_class_or_def_node(child)
        and _has_leading_comment_lines_in_prefix(first)
        and prev_is_import
        and (prev_import_in_lines_set or prefix_lines.intersection(lines_set))
    ):
      added_lines.add(first.lineno)

    prev_is_import = nodes_mod.is_import(first)
    prev_import_in_lines_set = bool(
        prev_is_import and first.lineno in lines_set
    )
  return added_lines


def _get_prefix_line_range(first: nodes_mod.Leaf) -> set[int]:
  """Returns the line range of first.prefix."""
  if not first.prefix:
    return set()
  prefix_lines = first.prefix.split("\n")
  start_lineno = first.lineno - len(prefix_lines) + 1
  return set(range(start_lineno, first.lineno))


def _has_leading_comment_lines_in_prefix(node: nodes_mod.Leaf) -> bool:
  """Returns True if there is a comment directly above the first."""
  if "#" not in node.prefix:
    return False
  prefix_lines = node.prefix.split("\n")
  return len(prefix_lines) >= 2 and prefix_lines[-2].lstrip().startswith("#")


def _is_class_or_def_node(node: nodes_mod.LN) -> bool:
  """Checks if node represents a (decorated) class or function definition."""
  return node.type in {
      pygram.python_symbols.classdef,
      pygram.python_symbols.funcdef,
      pygram.python_symbols.async_funcdef,
      pygram.python_symbols.decorated,
  }
