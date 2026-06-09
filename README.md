# JSON Typed Accessor With Extra Long Name

Extract data from JSON with type checking.

Usage:

```python
from python_json_typed_accessor_with_extra_long_name import (
    MissingKeyError,
    TypedAccessor,
    TypedAccessorError,
)

json_data = {"a": ["b", "c"], "d": ["e", "f"]}
accessor = TypedAccessor(json_data)
# getting values
child_a = accessor.extract_list("a")
print(child_a.extract_str(0))  # outputs b
try:
    child_a.extract_int(1)
except TypedAccessorError as type_error:
    print(type_error.args[0])  # outputs Not an int 1, got <class 'str'>
# list iteration
child_d = accessor.extract_list("d")
for key in child_d.get_remaining_keys():
    print(child_d.extract_str(key))  # outputs e, f
# checking for unknown keys
accessor.assert_empty()
# only one access per key is allowed
try:
    accessor.extract_list("a")
except MissingKeyError as key_error:
    print(key_error.args[0])  # outputs Missing a
```
