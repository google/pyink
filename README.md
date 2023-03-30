*Pyink*, pronounced pī-ˈiŋk, is a Python formatter, forked from
*[Black](https://github.com/psf/black)* with a few different formatting
behaviors. We intend to keep rebasing on top of *Black*'s latest changes.

# Why *Pyink*?

We would love to adopt *Black*, but adopting it overnight is too disruptive to
the thousands of developers working in our monorepo. We also have other Python
tooling that assumes certain formatting, it would be a too big task to update
them all at once. We decided to maintain a few local patches to *Black* as a
medium-term solution, and release them as a separate tool called *Pyink*.

*Pyink* is intended to be an adoption helper, and we wish to remove as many
patches as possible in the future.

# What are the main differences?

*   Support only formatting selected line ranges, using the `--pyink-lines=`
    argument (see [psf/black#830](https://github.com/psf/black/issues/830)).

*   Support two-space indentation, using the `pyink-indentation` option.

*   Support inferring preferred quote style by calculating the majority in a
    file, using the `pyink-use-majority-quotes` option.

*   Do not wrap trailing pragma comments if the line exceeds the length only
    because of the pragma (see
    [psf/black#2843](https://github.com/psf/black/issues/2843)). Example

    ```python
    # Pyink:
    result = some_other_module._private_function(arg="value")  # pylint: disable=protected-access

    # Black:
    result = some_other_module._private_function(
        arg="value"
    )  # pylint: disable=protected-access
    ```

*   Do not wrap imports in parentheses and move them to separate lines (see
    [psf/black#3324](https://github.com/psf/black/issues/3324)). Example:

    ```python
    # Pyink:
    from very_long_top_level_package_name.sub_package.another_level import a_long_module

    # Black:
    from very_long_top_level_package_name.sub_package.another_level import (
        a_long_module,
    )
    ```

*   Prefer not breaking lines between immediately nested brackets (see
    [psf/black#1811](https://github.com/psf/black/issues/1811)). Example:

    ```python
    # Pyink:
    secrets = frozenset({
        1001,
        1002,
        1003,
        1004,
        1005,
        1006,
        1007,
        1008,
        1009,
    })

    # Black:
    secrets = frozenset(
        {
            1001,
            1002,
            1003,
            1004,
            1005,
            1006,
            1007,
            1008,
            1009,
        }
    )
    ```

*   Add an empty line between class statements without docstrings, and the first
    method. We expect we will simply remove this difference from *Pyink* at some
    point. Example:

    ```python
    # Pyink:
    class MyTest(unittest.TestCase):

        def test_magic(self):
            ...

    # Black:
    class MyTest(unittest.TestCase):
        def test_magic(self):
            ...
    ```

*   Module docstrings are formatted same as other docstrings (see
    [psf/black#3493](https://github.com/psf/black/issues/3493)).

*   Temporarily disabled the following _Black_ future style changes:

    *   https://github.com/psf/black/pull/2916
    *   https://github.com/psf/black/pull/2278

## Historical differences

These are differences that existed in the past. We have upstreamed them to
*Black* so they are now identical.

*   Wrap concatenated strings in parens for function arguments (see
    [psf/black#3292](https://github.com/psf/black/issues/3292)). Example:

    ```python
    # New:
    function_call(
        (
            " lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor"
            " incididunt ut labore et dolore magna aliqua Ut enim ad minim"
        ),
        " veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo",
    )

    # Old:
    function_call(
        " lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor"
        " incididunt ut labore et dolore magna aliqua Ut enim ad minim",
        " veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo",
    )
    ```

*   Prefer splitting right hand side of assignment statements
    (see [psf/black#1498](https://github.com/psf/black/issues/1498)). Example:

    ```python
    # New:
    some_dictionary["some_key"] = (
        some_long_expression_causing_long_line
    )

    # Old:
    some_dictionary[
        "some_key"
    ] = some_long_expression_causing_long_line
    ```

# How do I use *Pyink*?

Same as `black`, except you'll use `pyink`. All `black` command line options are
supported by `pyink`. To configure the options in the `pyproject.toml` file, you
need to put them in the `[tool.pyink]` section instead of `[tool.black]`.

There are also a few *Pyink* only options:

```
  --pyink / --no-pyink            Enable the Pyink formatting mode. Disabling
                                  it should behave the same as Black.
                                  [default: pyink]
  --pyink-indentation [2|4]       The number of spaces used for indentation.
                                  [default: 4]
  --pyink-lines START-END         Range of lines to format. Must be specified
                                  as "START-END", index is 1-based and
                                  inclusive on both ends.
  --pyink-use-majority-quotes     When normalizing string quotes, infer
                                  preferred quote style by calculating the
                                  majority in the file. Multi-line strings and
                                  docstrings are excluded from this as they
                                  always use double quotes.
```

## Is there a VS Code extension for *Pyink*?

No, but with a bit workaround, you can use the
[Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
extension. After installing *Pyink* and the extension, you can set these in VS
Code's `settings.json`:

```json
{
    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter"
    },
    "black-formatter.path": [
        "path/to/pyink"
    ]
}
```

## Can I use *Pyink* with the [pre-commit](https://pre-commit.com/) framework?

Yes! You can put the following in your `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/google/pyink
    rev: 23.3.0
    hooks:
      - id: pyink
        # It is recommended to specify the latest version of Python
        # supported by your project here, or alternatively use
        # pre-commit's default_language_version, see
        # https://pre-commit.com/#top_level-default_language_version
        language_version: python3.9
```

# Why the name?

We want a name with the same number of characters as *Black*, to make patching
easier. And squid ink is black.

# License

[MIT](./LICENSE)

# Contributing

See the [contribution guide](./CONTRIBUTING.md).

# Changelog

See [CHANGES.md](./CHANGES.md).

# Disclaimer

This is not an officially supported Google product.
