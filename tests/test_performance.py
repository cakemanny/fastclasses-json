from dataclasses import dataclass
from typing import List
import time

from fastclasses_json import dataclass_json


@dataclass_json
@dataclass
class Point:
    x: int
    y: int


@dataclass_json
@dataclass
class PointBox:
    xs: List[Point]


def test_long_list():

    box_data = {
        'xs': [
            {'x': x, 'y': y}
            for x in range(200)
            for y in range(200)
        ]
    }

    t0 = time.monotonic()

    PointBox.from_dict(box_data)

    t1 = time.monotonic()

    xs = []
    for item in box_data['xs']:
        xs.append(Point(item['x'], item['y']))
    PointBox(xs)

    t2 = time.monotonic()

    from_dict_time = t1 - t0
    manual_time = t2 - t1

    assert from_dict_time < 3 * manual_time
