from collections.abc import Callable
from json import JSONDecodeError, loads
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase


class TypedAccessorError(Exception):
    """Base class for all typed accessor errors."""


class MissingKeyError(TypedAccessorError):
    """Key is not found. Args [message: str, key: int | str]"""


class WrongTypeError(TypedAccessorError):
    """Wrong type of the value. Args [message: str, key: int | str, value: object]"""


class NoneValueError(WrongTypeError):
    """Found None value at non-nullable key. Args [message: str, key: int | str]"""


class UnprocessedKeyError(TypedAccessorError):
    """Not all keys were processed. Args [message: str, keys: list[int | str]]"""


class TypedAccessor:
    """Extract data from JSON with type checking."""

    def __init__(self, source: object):
        """
        Initialize the typed accessor. `source` is a data extracted from JSON,
        can be only dict or list containing bool, dict, float, int, list, None, str.
        You should not modify or access the source after initialization.
        Raises WrongTypeError if source is not a dict or list.
        """
        if not isinstance(source, dict) and not isinstance(source, list):
            raise WrongTypeError(
                "Not a list or dict, got %s" % (type(source),), "", source
            )
        self._source: dict | list = source
        self._keys: set[int | str] = set(
            source.keys() if isinstance(source, dict) else range(len(source))
        )

    def assert_empty(self) -> None:
        """
        Checks that all keys were extracted.
        Raises UnprocessedKeyError if not.
        """
        remaining_keys = self.get_remaining_keys()
        if remaining_keys:
            raise UnprocessedKeyError(
                "Not processed %s" % (",".join(map(str, remaining_keys[0:10])),),
                remaining_keys,
            )

    def extract_list(self, key: int | str) -> "TypedAccessor":
        """
        Extracts list value of the `key`.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a list.
        """
        result = self.extract_value(key)
        if not isinstance(result, list):
            raise WrongTypeError(
                "Not an list %s, got %s" % (key, type(result)), key, result
            )
        return self.__class__(result)

    def extract_list_nullable(self, key: int | str) -> "TypedAccessor | None":
        """
        Extracts list value of the `key` or None if value is None.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises WrongTypeError if value is not a list.
        """
        try:
            return self.extract_list(key)
        except NoneValueError:
            return None

    def extract_list_nullable_optional(self, key: int | str) -> "TypedAccessor | None":
        """
        Extracts list value of the `key` or None if value is None or key is missing.
        Raises WrongTypeError if value is not a list.
        """
        try:
            return self.extract_list(key)
        except MissingKeyError:
            return None
        except NoneValueError:
            return None

    def extract_list_optional(self, key: int | str) -> "TypedAccessor | None":
        """
        Extracts list value of the `key` or None if key is missing.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a list.
        """
        try:
            return self.extract_list(key)
        except MissingKeyError:
            return None

    def extract_bool(self, key: int | str) -> bool:
        """
        Extracts bool value of the `key`.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a bool.
        """
        result = self.extract_value(key)
        if not isinstance(result, bool):
            raise WrongTypeError(
                "Not a bool %s, got %s" % (key, type(result)), key, result
            )
        return result

    def extract_bool_nullable(self, key: int | str) -> bool | None:
        """
        Extracts bool value of the `key` or None if value is None.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises WrongTypeError if value is not a bool.
        """
        try:
            return self.extract_bool(key)
        except NoneValueError:
            return None

    def extract_bool_nullable_optional(self, key: int | str) -> bool | None:
        """
        Extracts bool value of the `key` or None if value is None or key is missing.
        Raises WrongTypeError if value is not a bool.
        """
        try:
            return self.extract_bool(key)
        except MissingKeyError:
            return None
        except NoneValueError:
            return None

    def extract_bool_optional(self, key: int | str) -> bool | None:
        """
        Extracts bool value of the `key` or None if key is missing.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a bool.
        """
        try:
            return self.extract_bool(key)
        except MissingKeyError:
            return None

    def extract_float(self, key: int | str) -> float:
        """
        Extracts float value of the `key`.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a float.
        """
        result = self.extract_value(key)
        if not isinstance(result, float) and not isinstance(result, int):
            raise WrongTypeError(
                "Not a float %s, got %s" % (key, type(result)), key, result
            )
        return float(result)

    def extract_float_nullable(self, key: int | str) -> float | None:
        """
        Extracts float value of the `key` or None if value is None.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises WrongTypeError if value is not a float.
        """
        try:
            return self.extract_float(key)
        except NoneValueError:
            return None

    def extract_float_nullable_optional(self, key: int | str) -> float | None:
        """
        Extracts float value of the `key` or None if value is None or key is missing.
        Raises WrongTypeError if value is not a float.
        """
        try:
            return self.extract_float(key)
        except MissingKeyError:
            return None
        except NoneValueError:
            return None

    def extract_float_optional(self, key: int | str) -> float | None:
        """
        Extracts float value of the `key` or None if key is missing.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a float.
        """
        try:
            return self.extract_float(key)
        except MissingKeyError:
            return None

    def extract_int(self, key: int | str) -> int:
        """
        Extracts int value of the `key`.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not an int.
        """
        result = self.extract_value(key)
        if not isinstance(result, int):
            raise WrongTypeError(
                "Not an int %s, got %s" % (key, type(result)), key, result
            )
        return result

    def extract_int_nullable(self, key: int | str) -> int | None:
        """
        Extracts int value of the `key` or None if value is None.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises WrongTypeError if value is not an int.
        """
        try:
            return self.extract_int(key)
        except NoneValueError:
            return None

    def extract_int_nullable_optional(self, key: int | str) -> int | None:
        """
        Extracts int value of the `key` or None if value is None or key is missing.
        Raises WrongTypeError if value is not an int.
        """
        try:
            return self.extract_int(key)
        except MissingKeyError:
            return None
        except NoneValueError:
            return None

    def extract_int_optional(self, key: int | str) -> int | None:
        """
        Extracts int value of the `key` or None if key is missing.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not an int.
        """
        try:
            return self.extract_int(key)
        except MissingKeyError:
            return None

    def extract_dict(self, key: int | str) -> "TypedAccessor":
        """
        Extracts dict value of the `key`.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a dict.
        """
        result = self.extract_value(key)
        if not isinstance(result, dict):
            raise WrongTypeError(
                "Not a dict %s, got %s" % (key, type(result)), key, result
            )
        return self.__class__(result)

    def extract_dict_nullable(self, key: int | str) -> "TypedAccessor | None":
        """
        Extracts dict value of the `key` or None if value is None.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises WrongTypeError if value is not a dict.
        """
        try:
            return self.extract_dict(key)
        except NoneValueError:
            return None

    def extract_dict_nullable_optional(self, key: int | str) -> "TypedAccessor | None":
        """
        Extracts dict value of the `key` or None if value is None or key is missing.
        Raises WrongTypeError if value is not a dict.
        """
        try:
            return self.extract_dict(key)
        except MissingKeyError:
            return None
        except NoneValueError:
            return None

    def extract_dict_optional(self, key: int | str) -> "TypedAccessor | None":
        """
        Extracts dict value of the `key` or None if key is missing.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a dict.
        """
        try:
            return self.extract_dict(key)
        except MissingKeyError:
            return None

    def extract_str(self, key: int | str) -> str:
        """
        Extracts str value of the `key`.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a str.
        """
        result = self.extract_value(key)
        if not isinstance(result, str):
            raise WrongTypeError(
                "Not a str %s, got %s" % (key, type(result)), key, result
            )
        return result

    def extract_str_nullable(self, key: int | str) -> str | None:
        """
        Extracts str value of the `key` or None if value is None.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises WrongTypeError if value is not a str.
        """
        try:
            return self.extract_str(key)
        except NoneValueError:
            return None

    def extract_str_nullable_optional(self, key: int | str) -> str | None:
        """
        Extracts str value of the `key` or None if value is None or key is missing.
        Raises WrongTypeError if value is not a str.
        """
        try:
            return self.extract_str(key)
        except MissingKeyError:
            return None
        except NoneValueError:
            return None

    def extract_str_optional(self, key: int | str) -> str | None:
        """
        Extracts str value of the `key` or None if key is missing.
        Raises NoneValueError if value is None.
        Raises WrongTypeError if value is not a str.
        """
        try:
            return self.extract_str(key)
        except MissingKeyError:
            return None

    def extract_value(self, key: int | str) -> object:
        """
        Extracts unknown type value of the `key`.
        Only one access per key is allowed.
        Raises MissingKeyError if no such key exists or key already extracted.
        Raises NoneValueError if value is None.
        """
        try:
            self._keys.remove(key)
            result = self._source[key]
        except LookupError:
            raise MissingKeyError("Missing %s" % (key,), key)
        if result is None:
            raise NoneValueError("None %s" % (key,), key)
        return result

    def get_remaining_keys(self) -> list[int | str]:
        """Returns a keys that was not yet extracted."""
        return list(sorted(self._keys))

    def has_key(self, key: int | str) -> bool:
        """Checks if the key is present and not yet extracted."""
        return key in self._keys


class ReadJsonError(TypedAccessorError):
    """Base class for all read JSON errors."""


class FileAccessError(ReadJsonError):
    """Any error from the file system."""


class BadEncodingError(ReadJsonError):
    """Wrong file content encoding."""


class BadJsonError(ReadJsonError):
    """Error in JSON format or file is not a JSON."""


class TooBigError(ReadJsonError):
    """File is too big for processing."""


def read_json(
    path: str | Path, /, *, encoding: str = "utf8", limit: int = 100_000_000
) -> TypedAccessor:
    """
    Read JSON from the `path`.
    Raises BadEncodingError if file encoding is not same as `encoding` argument.
    Raises BadJsonError if file content is not a valid JSON or not an array or object.
    Raises FileAccessError if file not exists or any other system error.
    Raises TooBigError if file size is greater than `limit` argument.
    """
    try:
        with open(path, "rb") as file:
            try:
                buffer = file.read(limit)
                if file.read(1):
                    raise TooBigError("Too big %s. More than %d bytes" % (path, limit))
                return TypedAccessor(loads(buffer.decode(encoding)))
            except JSONDecodeError as json_error:
                raise BadJsonError(
                    "Bad json in %s at %d:%d. %s"
                    % (
                        path,
                        json_error.lineno,
                        json_error.colno,
                        json_error.msg,
                    )
                )
            except TooBigError:
                raise
            except TypedAccessorError as type_error:
                raise BadJsonError(
                    "Bad json in %s. %s"
                    % (
                        path,
                        type_error.args[0],
                    )
                )
            except UnicodeError:
                raise BadEncodingError("Bad text encoding in %s" % (path,))
    except OSError as open_error:
        raise FileAccessError(
            "Can not read %s. [%d] %s"
            % (
                path,
                open_error.errno,
                open_error.strerror,
            )
        )


class TypedAccessorTest(TestCase):
    def test_init(self) -> None:
        test_list: list[tuple[str, object, bool]] = [
            ("fail for false", False, True),
            ("fail for float", 1.2, True),
            ("fail for int", 1, True),
            ("fail for none", None, True),
            ("fail for object", set(), True),
            ("fail for str", "a", True),
            ("fail for true", True, True),
            ("pass for empty dict", {}, False),
            ("pass for empty list", [], False),
            ("pass for filled dict", {"a": 1, "b": 2}, False),
            ("pass for filled list", [1, 2], False),
        ]
        for test in test_list:
            with self.subTest("should %s" % (test[0],)):
                if test[2]:
                    with self.assertRaises(TypedAccessorError):
                        TypedAccessor(test[1])
                else:
                    self.assertIsInstance(TypedAccessor(test[1]), TypedAccessor)

    def test_assert_empty(self) -> None:
        test_list: list[tuple[str, object, list[int | str], bool]] = [
            ("fail for filled dict", {"a": 1}, [], True),
            ("fail for filled list", [1], [], True),
            ("fail for unprocessed dict", {"a": 1, "b": 2}, "a", True),
            ("fail for unprocessed list", [1, 2], [0], True),
            ("pass for empty dict", {}, [], False),
            ("pass for empty list", [], [], False),
            ("pass for processed dict", {"a": 1}, "a", False),
            ("pass for processed list", [1], [0], False),
        ]
        for test in test_list:
            with self.subTest("should %s" % (test[0],)):
                t = TypedAccessor(test[1])
                for key in test[2]:
                    t.extract_value(key)
                if test[3]:
                    with self.assertRaises(UnprocessedKeyError):
                        t.assert_empty()
                else:
                    t.assert_empty()
                    self.assertTrue(True)

    def _test_extract(
        self,
        method: Callable,
        value: object,
        /,
        *,
        nullable: bool = False,
        optional: bool = False,
        typecheck: bool = True,
    ) -> None:
        for test in self.provide_extract_tests(
            value,
            nullable=nullable,
            optional=optional,
            typecheck=typecheck,
        ):
            with self.subTest(
                "%s should %s" % (getattr(method, "__name__", repr(method)), test[0])
            ):
                t = TypedAccessor(test[1])
                for check in test[2]:
                    expected = check[1]
                    if isinstance(expected, type) and issubclass(expected, Exception):
                        with self.assertRaises(expected):
                            method(t, check[0])
                    else:
                        result = method(t, check[0])
                        if isinstance(expected, list):
                            item = expected[0]
                            self.assertIsInstance(result, TypedAccessor)
                            self.assertIs(item, result.extract_int(0))
                        elif isinstance(expected, dict):
                            item = expected["a"]
                            self.assertIsInstance(result, TypedAccessor)
                            self.assertIs(item, result.extract_int("a"))
                        else:
                            self.assertIs(expected, result)

    def test_extract(self) -> None:
        accessor = TypedAccessor
        test_list: list[tuple[Callable, object, bool, bool, bool]] = [
            (accessor.extract_bool, True, False, False, True),
            (accessor.extract_bool_nullable, True, True, False, True),
            (accessor.extract_bool_nullable_optional, True, True, True, True),
            (accessor.extract_bool_optional, True, False, True, True),
            (accessor.extract_dict, {"a": 42}, False, False, True),
            (accessor.extract_dict_nullable, {"a": 42}, True, False, True),
            (accessor.extract_dict_nullable_optional, {"a": 42}, True, True, True),
            (accessor.extract_dict_optional, {"a": 42}, False, True, True),
            (accessor.extract_float, 1.2, False, False, True),
            (accessor.extract_float_nullable, 1.2, True, False, True),
            (accessor.extract_float_nullable_optional, 1.2, True, True, True),
            (accessor.extract_float_optional, 1.2, False, True, True),
            (accessor.extract_int, 1, False, False, True),
            (accessor.extract_int_nullable, 1, True, False, True),
            (accessor.extract_int_nullable_optional, 1, True, True, True),
            (accessor.extract_int_optional, 1, False, True, True),
            (accessor.extract_list, [42], False, False, True),
            (accessor.extract_list_nullable, [42], True, False, True),
            (accessor.extract_list_nullable_optional, [42], True, True, True),
            (accessor.extract_list_optional, [42], False, True, True),
            (accessor.extract_str, "a", False, False, True),
            (accessor.extract_str_nullable, "a", True, False, True),
            (accessor.extract_str_nullable_optional, "a", True, True, True),
            (accessor.extract_str_optional, "a", False, True, True),
            (accessor.extract_value, 1, False, False, False),
        ]
        for test in test_list:
            self._test_extract(
                test[0],
                test[1],
                nullable=test[2],
                optional=test[3],
                typecheck=test[4],
            )

    @staticmethod
    def provide_extract_tests(
        value: object,
        /,
        *,
        nullable: bool = False,
        optional: bool = False,
        typecheck: bool = False,
    ) -> list[tuple[str, object, list[tuple[int | str, object]]]]:
        res: list[tuple[str, object, list[tuple[int | str, object]]]] = [
            ("extract from list", [value], [(0, value)]),
            ("extract from dict", {"a": value}, [("a", value)]),
        ]

        if nullable:
            res.append(("extract none in list", [None], [(0, None)]))
            res.append(("extract none in dict", {"a": None}, [("a", None)]))
        else:
            res.append(("fail for none in list", [None], [(0, NoneValueError)]))
            res.append(("fail for none in dict", {"a": None}, [("a", NoneValueError)]))

        if optional:
            res.append(("extract none for missing int in list", [], [(0, None)]))
            res.append(("extract none for missing str in list", [], [("a", None)]))
            res.append(("extract none for missing int in dict", {}, [(0, None)]))
            res.append(("extract none for missing str in dict", {}, [("a", None)]))
            res.append(
                (
                    "extract none for duplicate in list",
                    [value],
                    [(0, value), (0, None)],
                )
            )
            res.append(
                (
                    "extract none for duplicate in dict",
                    {"a": value},
                    [("a", value), ("a", None)],
                )
            )
        else:
            res.append(("fail for missing int in list", [], [(0, MissingKeyError)]))
            res.append(("fail for missing str in list", [], [("a", MissingKeyError)]))
            res.append(("fail for missing int in dict", {}, [(0, MissingKeyError)]))
            res.append(("fail for missing str in dict", {}, [("a", MissingKeyError)]))
            res.append(
                (
                    "fail for duplicate in list",
                    [value],
                    [(0, value), (0, MissingKeyError)],
                )
            )
            res.append(
                (
                    "fail for duplicate in dict",
                    {"a": value},
                    [("a", value), ("a", MissingKeyError)],
                )
            )

        if typecheck:
            res.append(("fail for wrong type", [set()], [(0, WrongTypeError)]))

        res.sort()

        return res

    def test_get_remaining_keys(self) -> None:
        test_list: list[tuple[str, object, list[int | str], list[object]]] = [
            ("be empty for empty dict", [], [], []),
            ("be empty for empty list", [], [], []),
            ("be empty for processed dict", {"a": 1}, ["a"], []),
            ("be empty for processed list", [1], [0], []),
            ("be sorted for dict", {"b": 2, "a": 1}, [], ["a", "b"]),
            ("be sorted for list", [2, 1], [], [0, 1]),
            ("get keys for dict", {"a": 1}, [], ["a"]),
            ("get keys for list", [1], [], [0]),
        ]
        for test in test_list:
            with self.subTest("should %s" % (test[0],)):
                t = TypedAccessor(test[1])
                for key in test[2]:
                    t.extract_value(key)
                self.assertEqual(test[3], t.get_remaining_keys())

    def test_has_key(self) -> None:
        test_list: list[tuple[str, object, list[int | str], int | str, bool]] = [
            ("be True if exists in list", [1], [], 0, True),
            ("be True if exists in dict", {"a": 1}, [], "a", True),
            ("be False if not exists in list", [1], [], 1, False),
            ("be False if not exists in dict", {"a": 1}, [], "b", False),
            ("be False after extraction in list", [1], [0], 0, False),
            ("be False after extraction in dict", {"a": 1}, ["a"], "a", False),
        ]
        for test in test_list:
            with self.subTest("should %s" % (test[0],)):
                t = TypedAccessor(test[1])
                for key in test[2]:
                    t.extract_value(key)
                self.assertIs(test[4], t.has_key(test[3]))


class ReadJsonTest(TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_read_json(self) -> None:
        test_list: list[
            tuple[str, str, bytes | None, str | None, int | None, object]
        ] = [
            ("fail if bad encoding", "t.json", b"\xff", "utf8", None, BadEncodingError),
            ("fail if bad json", "t.json", b"bad", None, None, BadJsonError),
            ("fail if directory", "", None, None, None, FileAccessError),
            ("fail if not exists", "no.json", None, None, None, FileAccessError),
            ("fail if too big", "t.json", b"[]", None, 1, TooBigError),
            ("fail if wrong type", "t.json", b"1", None, None, BadJsonError),
            ("read non-utf8", "t.json", b'["\xb8"]', "cp1251", None, "ё"),
            ("read utf8", "t.json", '["ё"]'.encode("utf8"), None, None, "ё"),
        ]
        for test in test_list:
            with self.subTest("should %s" % (test[0],)):
                path = Path(self.temp.name).joinpath(test[1])
                content = test[2]
                if content is not None:
                    with open(path, "wb") as file:
                        file.write(content)
                kwargs = {}
                encoding = test[3]
                if encoding is not None:
                    kwargs["encoding"] = encoding
                limit = test[4]
                if limit is not None:
                    kwargs["limit"] = limit
                expected = test[5]
                if isinstance(expected, type) and issubclass(expected, Exception):
                    with self.assertRaises(expected):
                        read_json(path, **kwargs)
                else:
                    result = read_json(path, **kwargs)
                    self.assertEqual(expected, result.extract_str(0))
