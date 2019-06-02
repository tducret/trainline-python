#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Little program to build a mini index station_id:station_name
from the official Trainline stations.csv"""

import pandas as pd
import io
import requests

_STATIONS_CSV_FILE = "https://raw.githubusercontent.com/\
trainline-eu/stations/master/stations.csv"

csv_content = requests.get(_STATIONS_CSV_FILE).content
df = pd.read_csv(io.StringIO(csv_content.decode('utf-8')),
                 sep=';', index_col=0, low_memory=False)
df = df[df.is_suggestable == 't']
df_mini = df.name.str.lower()
df_mini.to_csv("stations_mini.csv", sep=';', encoding='utf-8', header=False)
