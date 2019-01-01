#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for `trainline` package."""

# To be tested with : python3 -m pytest -vs tests/test_trainline.py

import pytest
import trainline
from trainline import Trainline, Trip, Passenger, Segment, ComfortClass, Folder
from datetime import date, timedelta


TOULOUSE_STATION_ID = "5311"
BORDEAUX_STATION_ID = "828"

_DEFAULT_COMFORT_CLASS_DICT = {
        "id": "ae9ba138a7c211e88f35afa2c1b6c287",
        "name": "pao.default",
        "description": "Un siège standard.",
        "title": "Normal",
        "options": {},
        "segment_id": "ae8b939ca7c211e8967edcf1e2aa0fd7",
        "condition_id": "ae9b9fbca7c211e893c6790139ba5461",
    }

_DEFAULT_SEGMENT_DICT = {
        "id": "ae8b939ca7c211e8967edcf1e2aa0fd7",
        "departure_date": "2018-10-15T08:49:00+02:00",
        "departure_station_id": TOULOUSE_STATION_ID,
        "arrival_date": "2018-10-15T10:58:00+02:00",
        "arrival_station_id": BORDEAUX_STATION_ID,
        "transportation_mean": "train",
        "carrier": "sncf",
        "train_number": "8202",
        "travel_class": "first",
        "trip_id": "f721ce4ca2cb11e88152d3a9f56d4f85",
        "comfort_class_ids": ["ae9ba138a7c211e88f35afa2c1b6c287"],
        "comfort_classes": [ComfortClass(mydict=_DEFAULT_COMFORT_CLASS_DICT)]
    }

_DEFAULT_TRIP_DICT = {
        "id": "f721ce4ca2cb11e88152d3a9f56d4f85",
        "departure_date": "2018-10-15T08:49:00+02:00",
        "departure_station_id": TOULOUSE_STATION_ID,
        "arrival_date": "2018-10-15T10:58:00+02:00",
        "arrival_station_id": BORDEAUX_STATION_ID,
        "price": 66.00,
        "currency": "EUR",
        "segment_ids": ["f721c960a2cb11e89a42408805033f41"],
        "segments": [Segment(mydict=_DEFAULT_SEGMENT_DICT)],
    }

_DEFAULT_FOLDER_DICT = {
        "id": "f721d0a4a2cb11e880abfc0416222638",
        "departure_date": "2018-10-15T08:49:00+02:00",
        "departure_station_id": TOULOUSE_STATION_ID,
        "arrival_date": "2018-10-15T10:58:00+02:00",
        "arrival_station_id": BORDEAUX_STATION_ID,
        "price": 66.00,
        "currency": "EUR",
        "trip_ids": ["f721ce4ca2cb11e88152d3a9f56d4f85"],
        "trips": [Trip(mydict=_DEFAULT_TRIP_DICT)],
    }


# Get the date of tomorrow for search tests,
# otherwise they will become obsolete in the future
tommorow_obj = date.today() + timedelta(days=1)
_TOMORROW = tommorow_obj.strftime("%d/%m/%Y")


def test_class_ComfortClass():
    cc = ComfortClass(mydict=_DEFAULT_COMFORT_CLASS_DICT)
    assert cc.id == "ae9ba138a7c211e88f35afa2c1b6c287"
    print()
    print(cc)


def test_class_Segment():
    seg = Segment(mydict=_DEFAULT_SEGMENT_DICT)
    assert seg.id == "ae8b939ca7c211e8967edcf1e2aa0fd7"
    print()
    print(seg)


def test_class_Folder():
    folder = Folder(mydict=_DEFAULT_FOLDER_DICT)
    assert folder.id == "f721d0a4a2cb11e880abfc0416222638"
    print()
    print(folder)


def test_class_Trip():
    trip = Trip(mydict=_DEFAULT_TRIP_DICT)
    assert trip.id == "f721ce4ca2cb11e88152d3a9f56d4f85"
    print()
    print(trip)


def test_class_Trip_errors():
    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["departure_station_id"] = 1234  # should be a string
        Trip(mydict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["price"] = "not_a_float"
        Trip(mydict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["departure_date"] = "not_a_date"
        Trip(mydict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["id"] = 12345  # string expected
        Trip(mydict=modified_trip_dict)

    with pytest.raises(TypeError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict.pop("id")  # delete a required parameter
        Trip(mydict=modified_trip_dict)

    with pytest.raises(ValueError):
        modified_trip_dict = _DEFAULT_TRIP_DICT.copy()
        modified_trip_dict["price"] = -1.50  # negative price impossible
        Trip(mydict=modified_trip_dict)


def test_class_Passenger():
    p1 = Passenger(birthdate="01/01/1980")
    print()
    print(p1)
    assert p1.birthdate == "01/01/1980"
    assert p1.cards == []
    age_p1 = date.today().year - 2018 + 38
    assert p1.age == age_p1
    id_p1 = p1.id
    assert len(id_p1) == 36
    assert p1.get_dict() == {
                              "id": id_p1,
                              "age": age_p1,
                              "cards": [],
                              "label": id_p1
                            }

    p2 = Passenger(birthdate="01/01/2006",
                   cards=[trainline.JEUNE, trainline.WEEK_END])
    print(p2)
    assert p2.birthdate == "01/01/2006"
    assert p2.cards == [trainline.JEUNE, trainline.WEEK_END]
    age_p2 = date.today().year - 2018 + 12
    assert p2.age == age_p2
    id_p2 = p2.id
    assert len(id_p2) == 36
    assert p2.get_dict() == {
                              "id": id_p2,
                              "age": age_p2,
                              "cards": [{"reference": trainline.JEUNE},
                                        {"reference": trainline.WEEK_END}],
                              "label": id_p2
                            }


def test_class_Passenger_errors():
    with pytest.raises(KeyError):
        Passenger(birthdate="01/03/2012", cards=["Unknown"])

    with pytest.raises(TypeError):
        Passenger(birthdate="not_a_date")

    with pytest.raises(TypeError):
        Passenger()


def test_get_station_id():
    station_id = trainline.get_station_id(station_name="Toulouse Matabiau")
    assert station_id == TOULOUSE_STATION_ID

    station_id = trainline.get_station_id(station_name="Bordeaux St-Jean")
    assert station_id == BORDEAUX_STATION_ID


def test_get_station_id_errors():
    with pytest.raises(KeyError):
        trainline.get_station_id(station_name="Unknown station")


def test_internal_search():
    t = Trainline()
    ret = t.search(
        departure_station_id=TOULOUSE_STATION_ID,
        arrival_station_id=BORDEAUX_STATION_ID,
        departure_date="2018-10-15T10:48:00+00:00",
        passenger_list=[Passenger(birthdate="01/01/1980").get_dict()])
    assert ret.status_code == 200


def test_basic_search():
    from_date = "{} 18:00".format(_TOMORROW)
    to_date = "{} 23:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Bordeaux St-Jean"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date)
    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)


def test_basic_search_Carcassonne():
    from_date = "{} 18:00".format(_TOMORROW)
    to_date = "{} 23:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Carcassonne"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date)
    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)


def test_basic_search_Paris():
    from_date = "{} 08:00".format(_TOMORROW)
    to_date = "{} 23:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Paris"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date)
    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)


def test_search_only_bus():
    from_date = "{} 09:00".format(_TOMORROW)
    to_date = "{} 15:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Bordeaux St-Jean"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date,
        transportation_mean="coach")
    print()
    print("Search BUS trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)

    for folder in results:
        for trip in folder.trips:
            for segment in trip.segments:
                assert(segment.transportation_mean == "coach")


def test_basic_search_with_bicyle():
    from_date = "{} 08:00".format(_TOMORROW)
    to_date = "{} 23:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Narbonne"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date,
        bicycle_with_or_without_reservation=True)
    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)


def test_basic_search_with_bicyle_without_reservation():
    from_date = "{} 08:00".format(_TOMORROW)
    to_date = "{} 23:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Carcassonne"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date,
        bicycle_without_reservation_only=True)
    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)
    #print(results.csv())


def test_basic_search_with_bicyle_with_reservation():
    from_date = "{} 08:00".format(_TOMORROW)
    to_date = "{} 23:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Bordeaux St-Jean"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date,
        bicycle_with_reservation_only=True)
    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)


def display_trips(folder_list):
    print(folder_list.csv())
    # for folder in folder_list:
    #     print()
    #     print("-----------------------")
    #     print(folder)
    #     for trip in folder.trips:
    #         print('\t', end='')
    #         print(trip)
    #         for segment in trip.segments:
    #             print('\t\t', end='')
    #             print(segment)
    #             for comfort_class in segment.comfort_classes:
    #                 print('\t\t\t', end='')
    #                 print(comfort_class)
    #                 for extra in comfort_class.extras:
    #                     print('\t\t\t\t', end='')
    #                     print("{} : {} {}".format(
    #                         extra.get("title"),
    #                         float(extra.get("cents"))/100,
    #                         extra.get("currency")))


def test_search_3_passengers_and_bicyles():
    Pierre = Passenger(birthdate="01/01/1980")
    Sophie = Passenger(birthdate="01/02/1981")
    Enzo = Passenger(birthdate="01/03/2012", cards=[trainline.ENFANT_PLUS])

    from_date = "{} 08:00".format(_TOMORROW)
    to_date = "{} 19:00".format(_TOMORROW)
    departure_station = "Toulouse Matabiau"
    arrival_station = "Bordeaux St-Jean"

    results = trainline.search(
        passengers=[Pierre, Sophie, Enzo],
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date,
        bicycle_with_or_without_reservation=True)

    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)

    csv_header = results.csv().split("\n")[0]
    assert csv_header == "departure_date;arrival_date;duration;\
number_of_segments;price;currency;transportation_mean;bicycle_reservation"

    # Check that the result trips starts at the proper date (tomorrow)
    first_result = results.csv().split("\n")[1]
    assert _TOMORROW in first_result.split(";")[0]

    last_result = results.csv().split("\n")[-2]
    assert _TOMORROW in last_result.split(";")[0]


def test_class_Trainline():
    t = Trainline()
    assert t is not None


def test_with_benerail():
    # Added this test to check that "benerail.default" comfort class
    # is handled properly ("options" field is missing in this case)
    # that was causing the issue #1
    from_date = "{} 08:00".format(_TOMORROW)
    to_date = "{} 23:00".format(_TOMORROW)
    departure_station = "Paris"
    arrival_station = "Antwerpen-Centraal"

    results = trainline.search(
        departure_station=departure_station,
        arrival_station=arrival_station,
        from_date=from_date,
        to_date=to_date)
    print()
    print("Search trips for {} to {}, between {} and {}".format(
        departure_station, arrival_station, from_date, to_date))
    print("{} results".format(len(results)))
    assert len(results) > 0

    display_trips(results)
