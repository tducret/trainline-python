# -*- coding: utf-8 -*-

"""Top-level package for Trainline."""

import requests
from requests import ConnectionError

__author__ = """Thibault Ducret"""
__email__ = 'hello@tducret.com'
__version__ = '0.0.1'


class Client(object):
    """ Do the requests with the servers """
    def __init__(self):
        self.session = requests.session()
        self.headers = {
                    'Host': 'myhost.com',
                    'User-Agent': 'User agent',
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


class MyClass(object):
    """ Class to... """
    def __init__(self, param1, list1, dict1):
        self.param1 = param1
        self.list1 = list1
        self.dict1 = dict1

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
