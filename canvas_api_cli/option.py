import typing as t

T = t.TypeVar("T")
U = t.TypeVar("U")


class Nothing:
    def __init__(self):
        pass

    def __str__(self):
        return "Nothing()"

    def __or__(self, f) -> "Nothing":
        return self.bind(f)

    def get(self):
        return None

    def bind(self, f) -> "Nothing":
        return self


class Some(t.Generic[T]):
    def __init__(self, value: T):
        self.value: T = value

    def __str__(self):
        return f"Some({self.value})"

    def __or__(
        self,
        f: t.Callable[[T], Nothing | U],
    ) -> t.Union[Nothing, "Some[U]"]:
        return self.bind(f)

    def get(self) -> T:
        return self.value

    def bind(
        self,
        f: t.Callable[[T], Nothing | U],
    ) -> t.Union[Nothing, "Some[U]"]:
        result = f(self.value)
        if result is None:
            return Nothing()
        if isinstance(result, Nothing):
            return result
        return Some(result)


Option = Nothing | Some[T]


def option(val: T | None) -> Nothing | Some[T]:
    if val is None:
        return Nothing()
    return Some(val)
