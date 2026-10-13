# flags: --unstable --minimum-version=3.13
# wrap a long string return annotation in parens, but don't split the string
def frobnicate() -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# with parameters, split the parameters rather than the string
def frobnicate(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass

# don't split strings followed by pragmas
def with_type_ignore(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # type: ignore
    pass

def with_fmt_skip(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # fmt: skip
    pass

# don't try to split strings without spaces
def with_unsplittable_string(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassNameWithoutAnySpacesWhatsoeverAndEvenMoreCharacters":
    pass

# don't split strings in parameter, subscript, or variable type annotations
def func_single_string_annotations(
    param: "ThisIsAVeryLongTypeAnnotationInAParameter | AnotherVeryLongTypeAnnotationInAParameter",
    *args: Set["ThisIsAVeryLongTypeAnnotationInStarArgs | AnotherVeryLongTypeAnnotationInStarArgs"],
    **kwargs: Set["ThisIsAVeryLongTypeAnnotationInKwargs | AnotherVeryLongTypeAnnotationInKwargs"],
) -> Set["ThisIsAVeryLongTypeAnnotationInSubscript | AnotherVeryLongTypeAnnotationInSubscript"]:
    x: "ThisIsAVeryLongTypeAnnotationInAnnAssign | AnotherVeryLongTypeAnnotationInAnnAssign"
    y: Set["ThisIsAVeryLongTypeAnnotationInVarSubscript | AnotherVeryLongTypeAnnotationInVarSubscript"] = set()

class WithAnnotations:
    attr: Set["ThisIsAVeryLongTypeAnnotationInAClassBody | AnotherVeryLongTypeAnnotationInAClassBody"] = set()

# don't split strings in type parameter bounds and defaults or type aliases
def generic[T: Set["ThisIsAVeryLongBoundTypeAnnotationForTheTypeVar | AnotherVeryLongBoundTypeAnnotationForTheTypeVar"], *Ts = Set["ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar | AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"]](x: T) -> T:
    pass

type Alias = Set["ThisIsAVeryLongTypeAnnotationInATypeAlias | AnotherVeryLongTypeAnnotationInATypeAlias"]

# strings that are not annotations are still split
annotated: Final = "this is a very long string value that is not a type annotation and may still be split"

def with_default(a: int = Set["this is a very long default value that is not a type annotation and may still be split"]) -> None:
    return Set["this is a very long return value that is not a type annotation and may still be split"]

# output

# wrap a long string return annotation in parens, but don't split the string
def frobnicate() -> (
    "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]"
):
    pass


# with parameters, split the parameters rather than the string
def frobnicate(
    a,
) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":
    pass


# don't split strings followed by pragmas
def with_type_ignore(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # type: ignore
    pass


def with_fmt_skip(a) -> "ThisIsTrulyUnreasonablyExtremelyLongClassName | list[ThisIsTrulyUnreasonablyExtremelyLongClassName]":  # fmt: skip
    pass


# don't try to split strings without spaces
def with_unsplittable_string(
    a,
) -> "ThisIsTrulyUnreasonablyExtremelyLongClassNameWithoutAnySpacesWhatsoeverAndEvenMoreCharacters":
    pass


# don't split strings in parameter, subscript, or variable type annotations
def func_single_string_annotations(
    param: "ThisIsAVeryLongTypeAnnotationInAParameter | AnotherVeryLongTypeAnnotationInAParameter",
    *args: Set[
        "ThisIsAVeryLongTypeAnnotationInStarArgs | AnotherVeryLongTypeAnnotationInStarArgs"
    ],
    **kwargs: Set[
        "ThisIsAVeryLongTypeAnnotationInKwargs | AnotherVeryLongTypeAnnotationInKwargs"
    ],
) -> Set[
    "ThisIsAVeryLongTypeAnnotationInSubscript | AnotherVeryLongTypeAnnotationInSubscript"
]:
    x: "ThisIsAVeryLongTypeAnnotationInAnnAssign | AnotherVeryLongTypeAnnotationInAnnAssign"
    y: Set[
        "ThisIsAVeryLongTypeAnnotationInVarSubscript | AnotherVeryLongTypeAnnotationInVarSubscript"
    ] = set()


class WithAnnotations:
    attr: Set[
        "ThisIsAVeryLongTypeAnnotationInAClassBody | AnotherVeryLongTypeAnnotationInAClassBody"
    ] = set()


# don't split strings in type parameter bounds and defaults or type aliases
def generic[
    T: Set[
        "ThisIsAVeryLongBoundTypeAnnotationForTheTypeVar | AnotherVeryLongBoundTypeAnnotationForTheTypeVar"
    ],
    *Ts = Set[
        "ThisIsAVeryLongDefaultTypeAnnotationForTheTypeVar | AnotherVeryLongDefaultTypeAnnotationForTheTypeVar"
    ],
](
    x: T,
) -> T:
    pass


type Alias = Set[
    "ThisIsAVeryLongTypeAnnotationInATypeAlias | AnotherVeryLongTypeAnnotationInATypeAlias"
]

# strings that are not annotations are still split
annotated: Final = (
    "this is a very long string value that is not a type annotation and may still be"
    " split"
)


def with_default(
    a: int = Set[
        "this is a very long default value that is not a type annotation and may still"
        " be split"
    ],
) -> None:
    return Set[
        "this is a very long return value that is not a type annotation and may still"
        " be split"
    ]
