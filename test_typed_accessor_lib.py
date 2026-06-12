from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from typed_accessor_lib import BadEncodingError
from typed_accessor_lib import BadJsonError
from typed_accessor_lib import FileAccessError
from typed_accessor_lib import MissingKeyError
from typed_accessor_lib import NoneValueError
from typed_accessor_lib import TooBigError
from typed_accessor_lib import TypedAccessor
from typed_accessor_lib import TypedAccessorError
from typed_accessor_lib import UnprocessedKeyError
from typed_accessor_lib import WrongTypeError
from typed_accessor_lib import read_json


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
            tuple[str, str, bytes | None, str | None, int | None, type, object]
        ] = [
            ("bad encoding", "t.json", b"\xff", "utf8", None, None, BadEncodingError),
            ("bad json", "t.json", b"bad", None, None, None, BadJsonError),
            ("directory", "", None, None, None, None, FileAccessError),
            ("not exists", "no.json", None, None, None, None, FileAccessError),
            ("too big", "t.json", b"[]", None, 1, None, TooBigError),
            ("wrong type", "t.json", b"1", None, None, None, BadJsonError),
            ("not dict", "t.json", b"[]", None, None, str, BadJsonError),
            ("not list", "t.json", b"{}", None, None, int, BadJsonError),
            ("non-utf8", "t.json", b'["\xb8"]', "cp1251", None, None, "ё"),
            ("utf8", "t.json", '["ё"]'.encode("utf8"), None, None, None, "ё"),
        ]
        for test in test_list:
            expected = test[6]
            fail = isinstance(expected, type) and issubclass(expected, Exception)
            do = "fail if" if fail else "read"
            with self.subTest("should %s %s" % (do, test[0])):
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
                key_type = test[5]
                if key_type is not None:
                    kwargs["key_type"] = key_type
                if fail:
                    with self.assertRaises(expected):
                        read_json(path, **kwargs)
                else:
                    result = read_json(path, **kwargs)
                    self.assertEqual(expected, result.extract_str(0))
