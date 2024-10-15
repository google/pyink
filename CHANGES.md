# Pyink Changelog

All notable changes to Pyink are recorded here.

## Unreleased

* Nothing notable unreleased.

## 24.10.0

This release is based on _Black_ v24.10.0.

* Add CLI option `--pyink-ipynb-indentation` to specify the number of spaces
  with which JSON content of Jupyter notebooks will be formatted.
* Add CLI option `--pyink-annotation-pragmas` to specify a list of annotation
  pragmas. Whenever any of them appears in a comment that line won't be split
  into multiple lines or joined with any other line.
* Fix formatting of Jupyter notebook cells with magic methods and any empty
  lines at the beginning or end of a cell.

## 24.8.0

This release is based on _Black_ v24.8.0.

## 24.3.0

This release is based on _Black_ v24.3.0.

* Remove the previously deprecated CLI option `--pyink-lines`. This was replaced
  by `--line-ranges`.

## 23.12.1

This release is based on _Black_ v23.12.1.

* The CLI option `--pyink-lines` is now deprecated and replaced by _Black_'s
  built-in option `--line-ranges`.
* Handle more trailing pragma cases so they are ignored for line-length
  calculation.

## 23.10.0

This release is based on _Black_ v23.10.0.

## 23.9.1

This release is based on _Black_ v23.9.1.

* _Black_ v23.9.9's new concise formatting for dummy implementations from
  [psf/black#3796](https://github.com/psf/black/pull/3796) is temporarily
  disabled for _Pyink_.

## 23.5.0

* Existing parentheses around strings are no longer removed if the content does
  not fit on a single line. This is related to
  https://github.com/psf/black/pull/3640 where we still want to keep the
  parentheses around the implicitly concatenated strings if the code already
  uses them, making it more obvious it's a single function argument.
* `--pyink-lines=` now works with stdin inputs (#16).
* Fixed compatibility issue on Python 3.7 (#13).

## 23.3.1

* In multiline module docstrings, trailing quotes that are put on their own line
  are now kept on their own line. (#8)

## 23.3.0

This release is based on _Black_ v23.3.0.

* _Pyink_ now requires _Black_ v23.3.0 (for blib2to3).

## 23.1.1

This release is based on https://github.com/psf/black/commit/9c8464ca7ddd48d1c19112d895ae12d783f01563.

* Fixed a bug where a module docstring ends with a line that's `LineLength-3`
  to `LineLength` long, an extra empty line was added.
* Fixed a bug when running *Pyink* on Python 3.8 and earlier (#3).
* Do not explode immediately nested literals that have a trailing comma in the
  body.

## 23.1.0

This release is based on _Black_ v23.1.0.

* Temporarily disabled the following _Black_ future style changes:
    * https://github.com/psf/black/pull/2916
    * https://github.com/psf/black/pull/2278
* Fixed a bug in incremental formatting (`--pyink_lines=`) where pairs of
  `# fmt: off/on` are used outside of the line ranges.
* Fixed a bug in incremental formatting (`--pyink_lines=`) when part of the
  match statement is changed.

## 22.12.0

This release is based on
https://github.com/psf/black/commit/96e62c57e3023977de177a8ba34678007a63f1fe
(two bugfix commits ahead of _Black_ v22.12.0).

* Prefer splitting right hand side of assignment statements
  (see [psf/black#1498](https://github.com/psf/black/issues/1498), this is being
  upstreamed in [psf/black/pull/3368](https://github.com/psf/black/pull/3368)).

## 22.10.0

* Initial release based on _Black_ v22.10.0.
