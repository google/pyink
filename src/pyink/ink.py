"""Module that contains Pyink specific additions to Black.

This is a separate module for easier patch management.
"""

import copy
import re
from typing import Any

from blib2to3 import pytree
from blib2to3.pgen2 import token
from pyink import lines as lines_mod
from pyink import mode
from pyink import nodes as nodes_mod
from pyink import strings


def majority_quote(node: nodes_mod.LN) -> mode.Quote:
  """Returns the majority quote from the node.

  Triple quoted strings are excluded from calculation. Quotes inside f-strings
  are also not counted. If the counts of double and single quotes are the
  same, it returns double quote.

  Args:
    node: A graph node of Python code split by operations.

  Returns:
    The majority quote of the node.
  """
  num_double_quotes = 0
  num_single_quotes = 0
  stack = [node]
  while stack:
    current_node = stack.pop()
    if isinstance(current_node, nodes_mod.Leaf) and (
        current_node.type == token.STRING
        or current_node.type == token.FSTRING_START
    ):
      value = current_node.value.lstrip(strings.STRING_PREFIX_CHARS)
      if value.startswith(("'''", '"""')):
        continue
      if value.startswith('"'):
        num_double_quotes += 1
      else:
        num_single_quotes += 1
      continue

    # Quotes of potential strings nested inside an f-string are not counted.
    if pytree.type_repr(current_node.type) == "fstring":
      stack.append(current_node.children[0])
    else:
      stack.extend(current_node.children)

  if num_single_quotes > num_double_quotes:
    return mode.Quote.SINGLE
  return mode.Quote.DOUBLE


def deepcopy_line(line: lines_mod.Line) -> lines_mod.Line:
  """Calculates a deep copy of a Line object.

  Deep-copying a Line object is not trivial because it contains various
  dictionaries mapping id(NL) -> NL, where NL stands for Node or Leaf. Because
  all objects are copied, also the ids in dictionaries need to be updated.

  The function first finds all NL objects and calculates the id mapping. Then
  it updates all dictionaries.

  Args:
    line: The Line object to copy.

  Returns:
    A deep copy of the Line object with updated references.
  """
  memo: dict[int, Any] = {}
  line_copy = copy.deepcopy(line, memo=memo)

  line_copy.comments = {
      id(memo[leaf_id]): comment_leaves
      for leaf_id, comment_leaves in line_copy.comments.items()
  }
  line_copy.bracket_tracker.delimiters = {
      id(memo[leaf_id]): priority
      for leaf_id, priority in line_copy.bracket_tracker.delimiters.items()
  }

  return line_copy
