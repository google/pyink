"""Module that contains Pyink specific additions to line range formatting.

This is a separate module for easier patch management.
"""

from collections.abc import Iterator
from blib2to3 import pygram
from blib2to3.pgen2 import token
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
  added_lines: set[int] = set()
  for expansion_func in (
      _expand_lines_set_for_leading_comments,
      _expand_lines_set_for_nested_defs,
      _expand_lines_set_for_class_docstrings,
  ):
    added_lines.update(expansion_func(src_node, lines_set))
  return added_lines


def _expand_lines_set_for_leading_comments(
    src_node: nodes_mod.Node, lines_set: set[int]
) -> set[int]:
  """Expands lines to include the first line of a top-level class/def.

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


def _expand_lines_set_for_nested_defs(
    src_node: nodes_mod.Node, lines_set: set[int]
) -> set[int]:
  """Expands lines to include both outer and inner definitions.

  Example:
  ```
  def foo():
    def bar():
      pass
  ```
  If lines_set contains `def bar():` then add also the `def foo():` line to be
  formatted.

  Args:
    src_node: The source node to expand the lines set for.
    lines_set: The initial set of chosen line indices.

  Returns:
    Indices of new lines to which formatting should be applied as well.
  """
  added_lines = set()
  for node in _iter_node_and_children(src_node):
    if not _is_func_node(node):
      continue
    suite = _get_suite_node(node)
    if suite is None:
      continue
    stmts = _get_stmts_in_suite(suite)
    if not stmts or not _is_class_or_def_node(stmts[0]):
      continue
    if _get_header_line_range(stmts[0]).intersection(lines_set):
      added_lines.update(_get_def_linenos(node))
  return added_lines


def _expand_lines_set_for_class_docstrings(
    src_node: nodes_mod.Node, lines_set: set[int]
) -> set[int]:
  r"""Expands lines to include class and docstring lines before a statement.

  Example:
  ```
  class Foo:
    \"""This is a class docstring.\"""
    a: bool
  ```
  If lines_set contains the docstring line or the statement directly after it,
  format the `class Foo:` line and docstring line so that Pyink knows the
  docstring is inside a class and inserts a blank line after it.

  Args:
    src_node: The source node to expand the lines set for.
    lines_set: The initial set of chosen line indices.

  Returns:
    Indices of new lines to which formatting should be applied as well.
  """
  added_lines = set()
  for node in _iter_node_and_children(src_node):
    if not _is_class_node(node):
      continue
    suite = _get_suite_node(node)
    if suite is None:
      continue
    stmts = _get_stmts_in_suite(suite)
    if not stmts:
      continue
    doc_leaf = nodes_mod.first_leaf(stmts[0])
    if doc_leaf is None or not nodes_mod.is_docstring(doc_leaf):
      continue
    doc_lines = _get_leaf_line_range(doc_leaf)
    class_lines = _get_header_line_range(node)
    stmt2_lines = _get_header_line_range(stmts[1]) if len(stmts) > 1 else set()
    if (
        doc_lines.intersection(lines_set)
        or stmt2_lines.intersection(lines_set)
        or class_lines.intersection(lines_set)
    ):
      added_lines.update(_get_def_linenos(node))
      added_lines.update(doc_lines)
  return added_lines


def _iter_node_and_children(node: nodes_mod.LN) -> Iterator[nodes_mod.LN]:
  """Recursively yields node and all its descendant nodes."""
  yield node
  if isinstance(node, nodes_mod.Node):
    for child in node.children:
      yield from _iter_node_and_children(child)


def _get_inner_node(node: nodes_mod.LN) -> nodes_mod.LN:
  """Unwraps a decorated node to its inner definition node."""
  if node.type == pygram.python_symbols.decorated and isinstance(
      node, nodes_mod.Node
  ):
    return node.children[-1]
  return node


def _get_suite_node(node: nodes_mod.LN) -> nodes_mod.Node | None:
  """Finds the suite child of a class or function definition node."""
  inner = _get_inner_node(node)
  if isinstance(inner, nodes_mod.Node):
    for child in inner.children:
      if child.type == pygram.python_symbols.suite and isinstance(
          child, nodes_mod.Node
      ):
        return child
  return None


def _get_stmts_in_suite(suite: nodes_mod.Node) -> list[nodes_mod.LN]:
  """Returns all statement nodes in a suite."""
  stmts = []
  for child in suite.children:
    if child.type not in {token.NEWLINE, token.INDENT, token.DEDENT}:
      stmts.append(child)
  return stmts


def _get_def_linenos(node: nodes_mod.LN) -> set[int]:
  """Returns the line number(s) of the definition and its decorator if any."""
  linenos = set()
  first = nodes_mod.first_leaf(node)
  if first is not None:
    linenos.add(first.lineno)
  inner_first = nodes_mod.first_leaf(_get_inner_node(node))
  if inner_first is not None:
    linenos.add(inner_first.lineno)
  return linenos


def _get_header_line_range(node: nodes_mod.LN) -> set[int]:
  """Returns the line range of the definition header (before the suite)."""
  lines = set()
  for leaf in node.leaves():
    lines.update(_get_leaf_line_range(leaf))
    if leaf.type == token.COLON:
      break
  return lines


def _get_leaf_line_range(leaf: nodes_mod.Leaf) -> set[int]:
  """Returns the line range occupied by leaf, including multiline value and prefix."""
  nl_count = leaf.value.count("\n")
  leaf_lines = set(range(leaf.lineno, leaf.lineno + nl_count + 1))
  return leaf_lines.union(_get_prefix_line_range(leaf))


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

def _is_class_node(node: nodes_mod.LN) -> bool:
  """Checks if node represents a (decorated) class definition."""
  return node.type == pygram.python_symbols.classdef or (
      node.type == pygram.python_symbols.decorated
      and node.children[-1].type == pygram.python_symbols.classdef
  )


_FUNC_NODE_TYPES = frozenset({
    pygram.python_symbols.funcdef,
    pygram.python_symbols.async_funcdef,
})


def _is_func_node(node: nodes_mod.LN) -> bool:
  """Checks if node represents a (decorated) function definition."""
  return node.type in _FUNC_NODE_TYPES or (
      node.type == pygram.python_symbols.decorated
      and node.children[-1].type in _FUNC_NODE_TYPES
  )


def _is_class_or_def_node(node: nodes_mod.LN) -> bool:
  """Checks if node represents a (decorated) class or function definition."""
  return _is_class_node(node) or _is_func_node(node)
