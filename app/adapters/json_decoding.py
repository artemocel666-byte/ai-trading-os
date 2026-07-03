import json
from decimal import Decimal
from typing import Any


def decode_json_with_decimal_numbers(content: bytes) -> Any:
    return json.loads(
        content,
        parse_float=Decimal,
        parse_int=Decimal,
        parse_constant=Decimal,
    )
