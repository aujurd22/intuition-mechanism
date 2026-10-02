def check(item) -> str:
    func, test_cases = item
    for args, expected in test_cases:
        try:
            result = func(*args)
            if isinstance(expected, type) and issubclass(expected, BaseException):
                return 'FAIL'
            if result != expected:
                return 'FAIL'
        except BaseException as e:
            if not (isinstance(expected, type) and issubclass(expected, BaseException) and isinstance(e, expected)):
                return 'FAIL'
    return 'PASS'

import json
item = json.loads('{"code": "def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')\n", "test": "assert count_vowels('ApplE') == 2\nassert count_vowels('XYZ') == 0\n"}')
result = check(item)
print(result)
