"""Module that contains Pyink specific additions to Black.

This is a separate module for easier patch management.
"""

import re

from blib2to3 import pytree
from blib2to3.pgen2 import token
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
