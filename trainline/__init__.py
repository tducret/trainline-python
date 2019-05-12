#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Top-level package for Trainline."""

import requests
from requests import ConnectionError
import json
from datetime import datetime, timedelta, date
import pytz
import time
import uuid
import os
import copy

__author__ = """Thibault Ducret"""
__email__ = 'hello@tducret.com'
__version__ = '0.0.8'

_SEARCH_URL = "https://www.trainline.eu/api/v5_1/search"
_DEFAULT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
_BIRTHDATE_FORMAT = '%d/%m/%Y'
_READABLE_DATE_FORMAT = "%d/%m/%Y %H:%M"
_DEFAULT_SEARCH_TIMEZONE = 'Europe/Paris'
_MAX_SERVER_RETRY = 3  # If a request is rejected, retry X times
_TIME_AFTER_FAILED_REQUEST = 10  # and wait Y seconds after a rejected request

ENFANT_PLUS = "SNCF.CarteEnfantPlus"
JEUNE = "SNCF.Carte1225"
WEEK_END = "SNCF.CarteEscapades"
SENIOR = "SNCF.CarteSenior"
TGVMAX = {"reference": "SNCF.HappyCard", "number": None}
_AVAILABLE_CARDS = [ENFANT_PLUS, JEUNE, WEEK_END, SENIOR]
_SPECIAL_CARDS = [TGVMAX]

_DEFAULT_PASSENGER_BIRTHDATE = "01/01/1980"

_SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
_STATIONS_CSV = os.path.join(_SCRIPT_PATH, "stations_mini.csv")


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
        trials = 0
        while trials <= _MAX_SERVER_RETRY:
            trials += 1
            ret = self.session.post(url=url,
                                    headers=self.headers,
                                    data=post_data)
            if (ret.status_code == expected_status_code):
                break
            else:
                time.sleep(_TIME_AFTER_FAILED_REQUEST)

        if (ret.status_code != expected_status_code):
            raise ConnectionError(
                'Status code {status} for url {url}\n{content}'.format(
                    status=ret.status_code, url=url, content=ret.text))
        return ret


class Trainline(object):
    """ Class to... """

    def __init__(self):
        pass

    def search(self, departure_station_id, arrival_station_id, departure_date,
               passenger_list):
        """ Search on Trainline """
        data = {
            "local_currency": "EUR",
            "search": {
                "passengers": passenger_list,
                "arrival_station_id": arrival_station_id,
                "departure_date": departure_date,
                "departure_station_id": departure_station_id,
                "systems": [
                    "sncf",
                    "db",
                    "idtgv",
                    "ouigo",
                    "trenitalia",
                    "ntv",
                    "hkx",
                    "renfe",
                    "cff",
                    "benerail",
                    "ocebo",
                    "westbahn",
                    "leoexpress",
                    "locomore",
                    "busbud",
                    "flixbus",
                    "distribusion",
                    "cityairporttrain",
                    "obb",
                    "timetable"
                ]
            }
        }
        post_data = json.dumps(data)
        c = Client()
        ret = c._post(url=_SEARCH_URL, post_data=post_data)
        return ret


class Folder(object):
    """ Class to represent a folder, composed of the trips of each passenger
    ex : Folder Paris-Toulouse : 65€, which contains 2 trips :
    - Trip Paris-Toulouse passenger1 : 45€ +
    - Trip Paris-Toulouse passenger2 : 20€
    """

    def __init__(self, mydict):
        expected = {
            "id": str,
            "departure_date": str,
            "departure_station_id": str,
            "arrival_date": str,
            "arrival_station_id": str,
            "price": float,
            "currency": str,
            "trip_ids": list,
            "trips": list,
        }

        for expected_param, expected_type in expected.items():
            param_value = mydict.get(expected_param)
            if type(param_value) is not expected_type:
                raise TypeError("Type {} expected for {}, {} received".format(
                    expected_type, expected_param, type(param_value)))
            setattr(self, expected_param, param_value)

        # Remove ':' in the +02:00 offset (=> +0200). It caused problem with
        # Python 3.6 version of strptime
        self.departure_date = _fix_date_offset_format(self.departure_date)
        self.arrival_date = _fix_date_offset_format(self.arrival_date)

        self.departure_date_obj = _str_datetime_to_datetime_obj(
            str_datetime=self.departure_date)
        self.arrival_date_obj = _str_datetime_to_datetime_obj(
            str_datetime=self.arrival_date)

        if len(self.trips) > 0:
            trip = self.trips[0]  # Choose trips[0] by default because every
            # trip of the folder has the same transportation mean and number
            # of segments
            self.transportation_mean = trip.transportation_mean
            self.segment_nb = len(trip.segments)

            if trip.bicycle_price is None:
                self.bicycle_reservation = "unavailable"
            else:
                self.bicycle_reservation = trip.bicycle_price

        if self.price < 0:
            raise ValueError("price cannot be < 0, {} received".format(
                self.price))

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ("[Folder] {} → {} : {} {} ({} trips) [id : {}]".format(
            self.departure_date, self.arrival_date, self.price, self.currency,
            len(self.trip_ids), self.id))

    def _main_characteristics(self):
        return ("{} → {} : {} {} ({} trips)".format(
            self.departure_date, self.arrival_date, self.price, self.currency,
            len(self.trip_ids)))

    # __hash__ and __eq__ methods are defined to allow to remove duplicates
    # in the results with list(set(folder_list))
    def __eq__(self, other):
        # If 2 folders have the same route and price, we consider that
        # they are the same, even if they don't have the same ids
        return self._main_characteristics() == other._main_characteristics()

    def __hash__(self):
        return hash((self._main_characteristics()))


class Trip(object):
    """ Class to represent a trip, composed of one or more segments """

    def __init__(self, mydict):
        expected = {
            "id": str,
            "departure_date": str,
            "departure_station_id": str,
            "arrival_date": str,
            "arrival_station_id": str,
            "price": float,
            "currency": str,
            "segment_ids": list,
            "segments": list,
        }

        for expected_param, expected_type in expected.items():
            param_value = mydict.get(expected_param)
            if type(param_value) is not expected_type:
                raise TypeError("Type {} expected for {}, {} received".format(
                    expected_type, expected_param, type(param_value)))
            setattr(self, expected_param, param_value)

        # Remove ':' in the +02:00 offset (=> +0200). It caused problem with
        # Python 3.6 version of strptime
        self.departure_date = _fix_date_offset_format(self.departure_date)
        self.arrival_date = _fix_date_offset_format(self.arrival_date)

        self.departure_date_obj = _str_datetime_to_datetime_obj(
            str_datetime=self.departure_date)
        self.arrival_date_obj = _str_datetime_to_datetime_obj(
            str_datetime=self.arrival_date)

        transportation_mean = []
        for segment in self.segments:
            transportation_mean.append(segment.transportation_mean)
        transportation_mean = list(set(transportation_mean))  # no duplicates
        self.transportation_mean = "+".join(transportation_mean)

        if self.price < 0:
            raise ValueError("price cannot be < 0, {} received".format(
                self.price))

        self.bicycle_price = 0  # Default
        for segment in self.segments:
            if segment.bicycle_price is not None:
                self.bicycle_price += segment.bicycle_price
            else:
                self.bicycle_price = None
                # Do not calculate price if at least one segment has no price
                break

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ("[Trip] {} → {} : {} {} ({} segments) [id : {}]".format(
            self.departure_date, self.arrival_date, self.price, self.currency,
            len(self.segment_ids), self.id))

    # __hash__ and __eq__ methods are defined to allow to remove duplicates
    # in the results with list(set(trip_list))
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id))


class Folders(object):
    """ Class to represent a list of folders """

    def __init__(self, folder_list):
        self.folders = folder_list

    def csv(self):
        csv_str = "departure_date;arrival_date;duration;number_of_segments;\
price;currency;transportation_mean;bicycle_reservation\n"
        for folder in self.folders:
            trip_duration = (folder.arrival_date_obj - folder.departure_date_obj)
            csv_str += "{dep};{arr};{dur};{seg};{price};{curr};\
{tr};{bicy}\n".format(
                dep=folder.departure_date_obj.strftime(_READABLE_DATE_FORMAT),
                arr=folder.arrival_date_obj.strftime(_READABLE_DATE_FORMAT),
                dur=_strfdelta(trip_duration, "{hours:02d}h{minutes:02d}"),
                seg=folder.segment_nb,
                price=str(folder.price).replace(".", ","),  # For French Excel
                curr=folder.currency,
                tr=folder.transportation_mean,
                bicy=str(folder.bicycle_reservation).replace(".", ","),
            )
        return csv_str

    def __len__(self):
        return len(self.folders)

    def __getitem__(self, key):
        """ Method to access the object as a list
        (ex : trips[1]) """
        return self.folders[key]


class Passenger(object):
    """ Class to represent a passenger """

    def __init__(self, birthdate, cards=[]):
        self.birthdate = birthdate
        self.birthdate_obj = _str_date_to_date_obj(
            str_date=self.birthdate,
            date_format=_BIRTHDATE_FORMAT)
        self.age = self._calculate_age()

        self.id = self._gen_id()

        for card in cards:
            if card not in _AVAILABLE_CARDS:
                raise KeyError("Card '{}' unknown, [{}] available".format(
                    card, ",".join(_AVAILABLE_CARDS)))
        self.cards = cards

    def _gen_id(self):
        """ Returns a unique passenger id in the proper format
        hhhhhhhh-hhhh-hhhh-hhhh-hhhhhhhhhhhh"""
        return str(uuid.uuid4())  # uuid4 = make a random UUID

    def _calculate_age(self):
        """ Returns the age (in years) from the birthdate """
        born = self.birthdate_obj
        today = date.today()
        age = today.year - born.year - \
              ((today.month, today.day) < (born.month, born.day))
        return age

    def get_dict(self):
        cards_dicts = []
        for card in self.cards:
            if type(card) is dict:
                cards_dicts.append(card)
                continue
            cards_dicts.append({"reference": card})

        passenger_dict = {
            "id": self.id,
            "age": self.age,
            "cards": cards_dicts,
            "label": self.id
        }
        return passenger_dict

    def __str__(self):
        return (repr(self))

    def __repr__(self):
        return ("[Passenger] birthdate={}, cards=[{}]".format(
            self.birthdate,
            ",".join(self.cards)))

    def add_special_card(self, card, number):
        if card not in _SPECIAL_CARDS:
            raise KeyError("Card '{}' unknown, [{}] available".format(
                card, ",".join([d['reference'] for d in _SPECIAL_CARDS])))
        c = copy.deepcopy(card)
        c['number'] = number
        self.cards.append(c)


class Segment(object):
    """ Class to represent a segment
    (a trip is composed of one or more segment) """

    def __init__(self, mydict):
        expected = {
            "id": str,
            "departure_date": str,
            "departure_station_id": str,
            "arrival_date": str,
            "arrival_station_id": str,
            "transportation_mean": str,
            "carrier": str,
            "train_number": str,
            "travel_class": str,
            "trip_id": str,
            "comfort_class_ids": list,
            "comfort_classes": list,
        }

        for expected_param, expected_type in expected.items():
            param_value = mydict.get(expected_param)
            if type(param_value) is not expected_type:
                raise TypeError("Type {} expected for {}, {} received".format(
                    expected_type, expected_param, type(param_value)))
            setattr(self, expected_param, param_value)

        # Remove ':' in the +02:00 offset (=> +0200). It caused problem with
        # Python 3.6 version of strptime
        self.departure_date = _fix_date_offset_format(self.departure_date)
        self.arrival_date = _fix_date_offset_format(self.arrival_date)

        self.departure_date_obj = _str_datetime_to_datetime_obj(
            str_datetime=self.departure_date)
        self.arrival_date_obj = _str_datetime_to_datetime_obj(
            str_datetime=self.arrival_date)

        self.bicycle_with_reservation = \
            self._check_extra_value("bicycle_with_reservation")
        self.bicycle_without_reservation = \
            self._check_extra_value("bicycle_without_reservation")

        self.bicycle_price = None

        for comfort_class in self.comfort_classes:
            if comfort_class.bicycle_price is not None:
                self.bicycle_price = comfort_class.bicycle_price

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ("[Segment] {} → {} : {} ({}) \
({} comfort_class) [id : {}]".format(
            self.departure_date, self.arrival_date,
            self.transportation_mean, self.carrier,
            len(self.comfort_class_ids), self.id))

    # __hash__ and __eq__ methods are defined to allow to remove duplicates
    # in the results with list(set(segment_list))
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id))

    def _check_extra_value(self, value):
        """ Returns True if the segment has an extra
        with the specified value """
        res = False
        for comfort_class in self.comfort_classes:
            for extra in comfort_class.extras:
                if extra.get("value", "") == value:
                    res = True
                    break
        return res


class ComfortClass(object):
    """ Class to represent a comfort_class
    (a trip is composed of one or more segment,
    each one composed of one or more comfort_class) """

    def __init__(self, mydict):
        expected = {
            "id": str,
            "name": str,
            "description": str,
            "title": str,
            "segment_id": str,
            "condition_id": str,
        }

        for expected_param, expected_type in expected.items():
            param_value = mydict.get(expected_param)
            if type(param_value) is not expected_type:
                raise TypeError("Type {} expected for {}, {} received".format(
                    expected_type, expected_param, type(param_value)))
            setattr(self, expected_param, param_value)

        self.options = mydict.get("options")
        if self.options is None:
            # No options field with "benerail.default" comfort class
            self.options = {}

        self.extras = self.options.get("extras")
        if self.extras is None:
            self.extras = []

        self.bicycle_price = None  # Default value
        for extra in self.extras:
            if ((extra.get("value", "") == "bicycle_with_reservation") or
                    (extra.get("value", "") == "bicycle_without_reservation")):
                self.bicycle_price = float(extra.get("cents")) / 100
                break

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ("[ComfortClass] {} ({}) ({} extras) [id : {}]".format(
            self.name,
            self.title,
            self.description,
            len(self.extras),
            self.id))

    # __hash__ and __eq__ methods are defined to allow to remove duplicates
    # in the results with list(set(comfort_class_list))
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash((self.id))


def _str_datetime_to_datetime_obj(str_datetime,
                                  date_format=_DEFAULT_DATE_FORMAT):
    """ Check the expected format of the string date and returns a datetime
    object """
    try:
        datetime_obj = datetime.strptime(str_datetime, date_format)
    except:
        raise TypeError("date must match the format {}, received : {}".format(
            date_format, str_datetime))
    if datetime_obj.tzinfo is None:
        tz = pytz.timezone(_DEFAULT_SEARCH_TIMEZONE)
        datetime_obj = tz.localize(datetime_obj)
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
    return date_str[:-3] + date_str[-2:]


def get_station_id(station_name):
    """ Returns the Trainline station id (mandatory for search) based on the
    stations csv file content, and the station_name passed in parameter """
    global _STATION_DB

    if '_STATION_DB' not in globals():
        _STATION_DB = _station_to_dict(_STATIONS_CSV)

    station_id = None
    for st_id, st_name in _STATION_DB.items():
        if st_name == station_name.lower().strip():
            station_id = st_id
            break

    if station_id is None:
        raise KeyError("'{}' station has not been found".format(station_name))

    return station_id


def search(departure_station, arrival_station,
           from_date, to_date,
           passengers=[Passenger(birthdate=_DEFAULT_PASSENGER_BIRTHDATE)],
           transportation_mean=None,
           bicycle_without_reservation_only=None,
           bicycle_with_reservation_only=None,
           bicycle_with_or_without_reservation=None,
           max_price=None):
    t = Trainline()

    departure_station_id = get_station_id(departure_station)
    arrival_station_id = get_station_id(arrival_station)

    from_date_obj = _str_datetime_to_datetime_obj(
        str_datetime=from_date, date_format=_READABLE_DATE_FORMAT)

    to_date_obj = _str_datetime_to_datetime_obj(
        str_datetime=to_date, date_format=_READABLE_DATE_FORMAT)

    passenger_list = []
    for passenger in passengers:
        passenger_list.append(passenger.get_dict())

    folder_list = []

    search_date = from_date_obj

    while True:

        last_search_date = search_date
        departure_date = search_date.strftime(_DEFAULT_DATE_FORMAT)

        ret = t.search(
            departure_station_id=departure_station_id,
            arrival_station_id=arrival_station_id,
            departure_date=departure_date,
            passenger_list=passenger_list)
        j = json.loads(ret.text)
        folders = _get_folders(search_results_obj=j)
        folder_list += folders

        # Check the departure date of the last trip found
        # If it is after the 'to_date', we can stop searching
        if folders[-1].departure_date_obj > to_date_obj:
            break
        else:
            search_date = folders[-1].departure_date_obj
            # If we get a date earlier than the last search date,
            # it means that we may be searching during the night,
            # so we must increment the search_date till we have a
            # trip posterior to 'to_date'
            # Probably the next day in this case
            if search_date <= last_search_date:
                search_date = last_search_date + timedelta(hours=4)
    folder_list = list(set(folder_list))  # Remove duplicate trips in the list

    # Filter the list
    bicycle_w_or_wout_reservation = bicycle_with_or_without_reservation
    _filter_folders_list = _filter_folders(
        folder_list=folder_list,
        from_date_obj=from_date_obj,
        to_date_obj=to_date_obj,
        transportation_mean=transportation_mean,
        bicycle_without_reservation_only=bicycle_without_reservation_only,
        bicycle_with_reservation_only=bicycle_with_reservation_only,
        bicycle_with_or_without_reservation=bicycle_w_or_wout_reservation,
        max_price=max_price)

    # Sort by date
    _filter_folders_list = sorted(_filter_folders_list,
                                  key=lambda folder: folder.departure_date_obj)

    folder_list_obj = Folders(_filter_folders_list)
    return folder_list_obj


def _convert_date_format(origin_date_str,
                         origin_date_format, target_date_format):
    """ Convert a date string to another format, for example :
    >>> print(_convert_date_format(origin_date_str="01/01/2002 08:00",\
origin_date_format="%d/%m/%Y %H:%M", target_date_format="%Y-%m-%dT%H:%M:%S%z"))
    2002-01-01T08:00:00+0100
    """
    date_obj = _str_datetime_to_datetime_obj(str_datetime=origin_date_str,
                                             date_format=origin_date_format)
    return date_obj.strftime(target_date_format)


def _get_folders(search_results_obj):
    """ Get folders from the json object of search results """
    trip_obj_list = _get_trips(search_results_obj)
    folders = search_results_obj.get("folders")
    folder_obj_list = []
    for folder in folders:
        dict_folder = {
            "id": folder.get("id"),
            "departure_date": folder.get("departure_date"),
            "departure_station_id": folder.get("departure_station_id"),
            "arrival_date": folder.get("arrival_date"),
            "arrival_station_id": folder.get("arrival_station_id"),
            "price": float(folder.get("cents")) / 100,
            "currency": folder.get("currency"),
            "trip_ids": folder.get("trip_ids"),
        }
        trips = []
        for trip_id in dict_folder["trip_ids"]:
            trip_found = _get_trip_from_id(
                trip_obj_list=trip_obj_list,
                trip_id=trip_id)
            if trip_found:
                trips.append(trip_found)
            else:
                # Remove the id if the object is invalid or not found
                dict_folder["trip_ids"].remove(trip_id)
        dict_folder["trips"] = trips

        folder_obj = Folder(dict_folder)
        folder_obj_list.append(folder_obj)
    return folder_obj_list


def _get_trips(search_results_obj):
    """ Get trips from the json object of search results """
    segment_obj_list = _get_segments(search_results_obj)
    trips = search_results_obj.get("trips")
    trip_obj_list = []
    for trip in trips:
        dict_trip = {
            "id": trip.get("id"),
            "departure_date": trip.get("departure_date"),
            "departure_station_id": trip.get("departure_station_id"),
            "arrival_date": trip.get("arrival_date"),
            "arrival_station_id": trip.get("arrival_station_id"),
            "price": float(trip.get("cents")) / 100,
            "currency": trip.get("currency"),
            "segment_ids": trip.get("segment_ids"),
        }
        segments = []
        for segment_id in dict_trip["segment_ids"]:
            segment_found = _get_segment_from_id(
                segment_obj_list=segment_obj_list,
                segment_id=segment_id)
            if segment_found:
                segments.append(segment_found)
            else:
                # Remove the id if the object is invalid or not found
                dict_trip["segment_ids"].remove(segment_id)
        dict_trip["segments"] = segments

        trip_obj = Trip(dict_trip)
        trip_obj_list.append(trip_obj)
    return trip_obj_list


def _get_trip_from_id(trip_obj_list, trip_id):
    """ Get a trip from a list, based on a trip id """
    found_trip_obj = None
    for trip_obj in trip_obj_list:
        if trip_obj.id == trip_id:
            found_trip_obj = trip_obj
            break
    return found_trip_obj


def _get_segments(search_results_obj):
    """ Get segments from the json object of search results """
    comfort_class_obj_list = _get_comfort_classes(search_results_obj)
    segments = search_results_obj.get("segments")
    segment_obj_list = []
    for segment in segments:
        comfort_class_ids = segment.get("comfort_class_ids")
        if comfort_class_ids is None:
            comfort_class_ids = []
        dict_segment = {
            "id": segment.get("id"),
            "departure_date": segment.get("departure_date"),
            "departure_station_id": segment.get("departure_station_id"),
            "arrival_date": segment.get("arrival_date"),
            "arrival_station_id": segment.get("arrival_station_id"),
            "transportation_mean": segment.get("transportation_mean"),
            "carrier": segment.get("carrier"),
            "train_number": segment.get("train_number"),
            "travel_class": segment.get("travel_class"),
            "trip_id": segment.get("trip_id"),
            "comfort_class_ids": comfort_class_ids,
        }
        comfort_classes = []
        for comfort_class_id in dict_segment["comfort_class_ids"]:
            comfort_class_found = _get_comfort_class_from_id(
                comfort_class_obj_list=comfort_class_obj_list,
                comfort_class_id=comfort_class_id)
            if comfort_class_found:
                comfort_classes.append(comfort_class_found)
            else:
                # Remove the id if the object is invalid or not found
                dict_segment["comfort_class_ids"].remove(comfort_class_id)
        dict_segment["comfort_classes"] = comfort_classes
        try:
            segment_obj = Segment(dict_segment)
            segment_obj_list.append(segment_obj)
        except TypeError:
            pass
            # Do not add a segment if it is not contain all the required fields
    return segment_obj_list


def _get_segment_from_id(segment_obj_list, segment_id):
    """ Get a segment from a list, based on a segment id """
    found_segment_obj = None
    for segment_obj in segment_obj_list:
        if segment_obj.id == segment_id:
            found_segment_obj = segment_obj
            break
    return found_segment_obj


def _get_comfort_classes(search_results_obj):
    """ Get comfort classes from the json object of search results """
    comfort_classes = search_results_obj.get("comfort_classes")
    if comfort_classes is None:
        comfort_classes = []
    comfort_class_obj_list = []
    for comfort_class in comfort_classes:
        description = comfort_class.get("description")
        if description is None:
            description = ""
        title = comfort_class.get("title")
        if title is None:
            title = ""
        dict_comfort_class = {
            "id": comfort_class.get("id"),
            "name": comfort_class.get("name"),
            "description": description,
            "title": title,
            "options": comfort_class.get("options"),
            "segment_id": comfort_class.get("segment_id"),
            "condition_id": comfort_class.get("condition_id"),
        }
        comfort_class_obj = ComfortClass(dict_comfort_class)
        comfort_class_obj_list.append(comfort_class_obj)
    return comfort_class_obj_list


def _get_comfort_class_from_id(comfort_class_obj_list, comfort_class_id):
    """ Get a comfort_class from a list, based on a comfort_class id """
    found_comfort_class_obj = None
    for comfort_class_obj in comfort_class_obj_list:
        if comfort_class_obj.id == comfort_class_id:
            found_comfort_class_obj = comfort_class_obj
            break
    return found_comfort_class_obj


def _filter_folders(folder_list, from_date_obj=None, to_date_obj=None,
                    min_price=0.0, max_price=None, transportation_mean=None,
                    min_segment_nb=1, max_segment_nb=None,
                    bicycle_without_reservation_only=None,
                    bicycle_with_reservation_only=None,
                    bicycle_with_or_without_reservation=None):
    """ Filter a list of folders, based on different attributes, such as
    from_date or min_price. Returns the filtered list """
    filtered_folder_list = []
    for folder in folder_list:
        to_be_filtered = False

        # Price
        if folder.price < min_price:
            to_be_filtered = True
        if max_price is not None:
            if folder.price > max_price:
                to_be_filtered = True

        # Date
        if from_date_obj:
            if folder.departure_date_obj < from_date_obj:
                to_be_filtered = True
        if to_date_obj:
            if folder.departure_date_obj > to_date_obj:
                to_be_filtered = True

        for trip in folder.trips:  # Check every trip

            # Transportation mean
            if transportation_mean:
                for segment in trip.segments:
                    if segment.transportation_mean != transportation_mean:
                        to_be_filtered = True
                        break

            # Number of segments
            if min_segment_nb:
                if len(trip.segments) < min_segment_nb:
                    to_be_filtered = True
            if max_segment_nb:
                if len(trip.segments) > max_segment_nb:
                    to_be_filtered = True

            # Bicycle
            # All segments of the trip must respect the bicycle conditions
            if bicycle_with_reservation_only:
                for segment in trip.segments:
                    if segment.bicycle_with_reservation != \
                            bicycle_with_reservation_only:
                        to_be_filtered = True
                        break

            if bicycle_without_reservation_only:
                for segment in trip.segments:
                    if segment.bicycle_without_reservation != \
                            bicycle_without_reservation_only:
                        to_be_filtered = True
                        break

            if bicycle_with_or_without_reservation:
                for segment in trip.segments:
                    condition = (segment.bicycle_with_reservation or
                                 segment.bicycle_without_reservation)
                    if condition != bicycle_with_or_without_reservation:
                        to_be_filtered = True
                        break

        # Add to list if it has not been filtered
        if not to_be_filtered:
            filtered_folder_list.append(folder)
    return filtered_folder_list


def _strfdelta(tdelta, fmt):
    """ Format a timedelta object """
    # Thanks to https://stackoverflow.com/questions/8906926
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def _read_file(filename):
    """ Returns the file content as as string """
    with open(filename, 'r', encoding='utf8') as f:
        read_data = f.read()
    return read_data


def _station_to_dict(filename, csv_delimiter=';'):
    """ Returns the stations csv database as a dict <id>:<station_name> """
    csv_content = _read_file(filename)
    station_dict = {}
    for line in csv_content.split("\n"):
        station_id = line.split(csv_delimiter)[0]
        station_name = csv_delimiter.join(line.split(csv_delimiter)[1:])
        station_dict[station_id] = station_name
    return station_dict
