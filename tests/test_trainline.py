#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `trainline` package."""

# To be tested with : python3 -m pytest -vs tests/test_trainline.py

import pytest
import os
from trainline import Trainline, Trip

# Get useful environment variables
VAR = os.environ.get('VAR', None)

TOULOUSE_STATION_ID = 5306
BORDEAUX_STATION_ID = 827

_DEFAULT_TRIP_DICT = {
        "id": "f721ce4ca2cb11e88152d3a9f56d4f85",
        "departure_date": "2018-10-15T08:49:00+02:00",
        "departure_station_id": 5311,
        "arrival_date": "2018-10-15T10:58:00+02:00",
        "arrival_station_id": 828,
        "price": 66.00,
        "currency": "EUR",
        "segment_ids": ["f721c960a2cb11e89a42408805033f41"],
    }


def test_class_Trip():
    trip = Trip(dict=_DEFAULT_TRIP_DICT)
    assert trip.id == "f721ce4ca2cb11e88152d3a9f56d4f85"


def test_class_Trip_errors():
    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["departure_station_id"] = "not_an_integer"
        Trip(dict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["price"] = "not_a_float"
        Trip(dict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["departure_date"] = "not_a_date"
        Trip(dict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["id"] = 12345  # string expected
        Trip(dict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict.pop("id")  # delete a required parameter
        Trip(dict=modified_trip_dict)

    with pytest.raises(ValueError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["price"] = -1.50  # negative price impossible
        Trip(dict=modified_trip_dict)


def test_class_Trainline():
    t = Trainline()
    assert t is not None


# def test_class_MyClass_errors():
#     with pytest.raises(KeyError):
#         MyClass(param1=1, param2="UNKNOWN")

#     with pytest.raises(TypeError):
#         MyClass(param1="abc", param2="abc")

#     with pytest.raises(ValueError):
#         MyClass(param2="abc")


def test_search():
    t = Trainline()
    ret = t.search(
        departure_station_id=TOULOUSE_STATION_ID,
        arrival_station_id=BORDEAUX_STATION_ID,
        departure_date="2018-10-15T10:48:00+00:00")
    assert ret.status_code == 200
