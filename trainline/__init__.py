# -*- coding: utf-8 -*-

"""Top-level package for Trainline."""

import requests
from requests import ConnectionError
import json
from datetime import datetime

__author__ = """Thibault Ducret"""
__email__ = 'hello@tducret.com'
__version__ = '0.0.1'

_SEARCH_URL = "https://www.trainline.eu/api/v5_1/search"
_DEFAULT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
_BIRTHDATE_FORMAT = '%d/%m/%Y'

ENFANT_PLUS = "ENFANT_PLUS"
JEUNE = "JEUNE"
_AVAILABLE_CARDS = [ENFANT_PLUS, JEUNE]


class Client(object):
    """ Do the requests with the servers """
    def __init__(self):
        self.session = requests.session()
        self.headers = {
                    'Accept': 'application/json',
                    'User-Agent': 'CaptainTrain/43(4302) Android/4.4.2(19)',
                    'Accept-Language': 'fr',
                    'Content-Type': 'application/json; charset=UTF-8',
                    'Host': 'www.trainline.eu',
                    }

    def _get(self, url, expected_status_code=200):
        ret = self.session.get(url=url, headers=self.headers)
        if (ret.status_code != expected_status_code):
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret

    def _post(self, url, post_data, expected_status_code=200):
        ret = self.session.post(url=url,
                                headers=self.headers,
                                data=post_data)
        if (ret.status_code != expected_status_code):
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret


class Trainline(object):
    """ Class to... """
    def __init__(self):
        pass

    def search(self, departure_station_id, arrival_station_id, departure_date):
        """ Search on Trainline """
        data = {
              "local_currency": "EUR",
              "search": {
                "passengers": [
                  {
                    "id": "90ec4e55-f6f1-4298-bb02-7dd88fe33fca",
                    "age": 26,
                    "cards": [],
                    "label": "90ec4e55-f6f1-4298-bb02-7dd88fe33fca"
                  }
                ],
                "arrival_station_id": arrival_station_id,
                "departure_date": departure_date,
                "departure_station_id": departure_station_id,
                "systems": [
                  "benerail",
                  "busbud",
                  "db",
                  "hkx",
                  "idtgv",
                  "locomore",
                  "ntv",
                  "ocebo",
                  "ouigo",
                  "ravel",
                  "renfe",
                  "sncf",
                  "timetable",
                  "trenitalia",
                  "westbahn",
                  "flixbus",
                  "pao_ouigo",
                  "pao_sncf",
                  "leoexpress",
                  "city_airport_train",
                  "obb",
                  "distribusion"
                ]
              }
            }
        post_data = json.dumps(data)
        c = Client()
        ret = c._post(url=_SEARCH_URL, post_data=post_data)
        return ret

    def _get_trips(self, search_results):
        j = json.loads(search_results)
        trips = j.get("trips")
        trip_obj_list = []
        for trip in trips:
            dict_trip = {
                "id": trip.get("id"),
                "departure_date": trip.get("departure_date"),
                "departure_station_id": trip.get("departure_station_id"),
                "arrival_date": trip.get("arrival_date"),
                "arrival_station_id": trip.get("arrival_station_id"),
                "price": trip.get("price"),
                "currency": trip.get("currency"),
                "segment_ids": trip.get("segment_ids"),
            }
            trip_obj = Trip(dict_trip)
            trip_obj_list.append(trip_obj)
        return trip_obj_list

    def get_param1(self):
        """ Get the param1 """
        return(self.param1)

    def __str__(self):
        return('{}'.format(self.param1))

    def __repr__(self):
        return("Myclass(param1={})".format(self.param1))

    def __len__(self):
        return len(self.list1)

    def __getitem__(self, key):
        """ Méthod to access the object as a list
        (ex : list1[1]) """
        return self.list[key]

    def __getattr__(self, attr):
        """ Method to access a dictionnary key as an attribute
        (ex : dict1.my_key) """
        return self.dict1.get(attr, "")


class Trip(object):
    """ Class to represent a trip, composed of one or more segments """
    def __init__(self, dict):
        expected = {
            "id": str,
            "departure_date": str,
            "departure_station_id": int,
            "arrival_date": str,
            "arrival_station_id": int,
            "price": float,
            "currency": str,
            "segment_ids": list,
        }

        for expected_param, expected_type in expected.items():
            param_value = dict.get(expected_param)
            if type(param_value) is not expected_type:
                raise TypeError("Type {} expected for {}, {} received".format(
                    expected_type, expected_param, type(param_value)))
            setattr(self, expected_param, param_value)

        # Remove ':' in the +02:00 offset (=> +0200). It caused problem with
        # Python 3.6 version of strptime
        self.departure_date = _fix_date_offset_format(self.departure_date)
        self.arrival_date = _fix_date_offset_format(self.arrival_date)

        self.departure_date_obj = _str_datetime_to_datetime_obj(
            self.departure_date)
        self.darrival_date_obj = _str_datetime_to_datetime_obj(
            self.arrival_date)

        if self.price < 0:
            raise ValueError("price cannot be < 0, {} received".format(
                self.price))

    def __str__(self):
        return('{}'.format(self.param1))

    def __repr__(self):
        return("Myclass(param1={})".format(self.param1))

    def __len__(self):
        return len(self.list1)

    def __getitem__(self, key):
        """ Méthod to access the object as a list
        (ex : list1[1]) """
        return self.list[key]

    def __getattr__(self, attr):
        """ Method to access a dictionnary key as an attribute
        (ex : dict1.my_key) """
        return self.dict1.get(attr, "")


class Passenger(object):
    """ Class to represent a passenger """
    def __init__(self, birthdate, cards=[]):
        self.birthdate = birthdate
        self.birthdate_obj = _str_date_to_date_obj(
            str_date=self.birthdate,
            date_format=_BIRTHDATE_FORMAT)

        for card in cards:
            if card not in _AVAILABLE_CARDS:
                raise KeyError("Card '{}' unknown, [{}] available".format(
                    card, ",".join(_AVAILABLE_CARDS)))
        self.cards = cards

    def __str__(self):
        return(repr(self))

    def __repr__(self):
        return("Passenger(birthdate={}, cards=[{}])".format(
            self.birthdate,
            ",".join(self.cards)))


def _str_datetime_to_datetime_obj(str_datetime,
                                  date_format=_DEFAULT_DATE_FORMAT):
    """ Check the expected format of the string date and returns a datetime
    object """
    try:
        datetime_obj = datetime.strptime(str_datetime, date_format)
    except:
        raise TypeError("date must match the format {}, received : {}".format(
            date_format, str_datetime))
    return datetime_obj


def _str_date_to_date_obj(str_date, date_format=_BIRTHDATE_FORMAT):
    """ Check the expected format of the string date and returns a datetime
    object """
    try:
        date_obj = datetime.strptime(str_date, date_format)
    except:
        raise TypeError("date must match the format {}, received : {}".format(
            date_format, str_date))
    return date_obj


def _fix_date_offset_format(date_str):
            """ Remove ':' in the UTC offset, for example :
            >>> print(_fix_date_offset_format("2018-10-15T08:49:00+02:00"))
            2018-10-15T08:49:00+0200
            """
            return date_str[:-3]+date_str[-2:]


def get_station_id(station_name):
    # TODO : Use trainline station database instead
    # https://github.com/trainline-eu/stations
    # https://raw.githubusercontent.com/trainline-eu/stations/master/stations.csv
    _AVAILABLE_STATIONS = {
        "Toulouse Matabiau": 5311,
        "Bordeaux St-Jean": 828,
    }
    return _AVAILABLE_STATIONS[station_name]
