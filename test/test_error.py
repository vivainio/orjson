# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import json
import unittest

import pytest

import orjson

ASCII_TEST = b"""\
{
  "a": "qwe",
  "b": "qweqwe",
  "c": "qweq",
  "d: "qwe"
}
"""

MULTILINE_EMOJI = """[
    "😊",
    "a"
"""


class JsonDecodeErrorTests(unittest.TestCase):
    def _test(self, data, expected_err_dict):
        with pytest.raises(json.decoder.JSONDecodeError) as json_exc_info:
            json.loads(data)

        json_err_dict = json_exc_info.value.__dict__

        with pytest.raises(json.decoder.JSONDecodeError) as orjson_exc_info:
            orjson.loads(data)

        orjson_err_dict = orjson_exc_info.value.__dict__

        for k in {"pos", "lineno", "colno"}:
            assert (
                json_err_dict[k] == orjson_err_dict[k] == expected_err_dict[k]
            ), f"{k!r} should be the same between stdlib `json` and `orjson`"

    def test_ascii(self):
        self._test(
            ASCII_TEST,
            {"pos": 55, "lineno": 5, "colno": 8},
        )

    def test_latin1(self):
        self._test(
            """["üýþÿ", "a" """,
            {"pos": 13, "lineno": 1, "colno": 14},
        )

    def test_two_byte_str(self):
        self._test(
            """["東京", "a" """,
            {"pos": 11, "lineno": 1, "colno": 12},
        )

    def test_two_byte_bytes(self):
        self._test(
            b'["\xe6\x9d\xb1\xe4\xba\xac", "a" ',
            {"pos": 11, "lineno": 1, "colno": 12},
        )

    def test_four_byte(self):
        self._test(
            MULTILINE_EMOJI,
            {"pos": 19, "lineno": 4, "colno": 1},
        )

    def test_tab(self):
        # data/jsonchecker/fail26.json
        self._test(
            """["tab\   character\   in\  string\  "]""",
            {"pos": 5, "lineno": 1, "colno": 6},
        )
