from json import JSONDecodeError, loads
from pathlib import Path


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
