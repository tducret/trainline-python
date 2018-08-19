# Trainline

[![Travis](https://img.shields.io/travis/tducret/trainline-python.svg)](https://travis-ci.org/tducret/trainline-python)
[![Coveralls github](https://img.shields.io/coveralls/github/tducret/trainline-python.svg)](https://coveralls.io/github/tducret/trainline-python)
[![PyPI](https://img.shields.io/pypi/v/trainline.svg)](https://pypi.org/project/trainline/)
![License](https://img.shields.io/github/license/tducret/trainline-python.svg)

## Description

Non-official Python wrapper and CLI tool for Trainline

# Requirements

- Python 3
- pip3

## Installation

```bash
pip3 install -U trainline
```

## Package usage

```python
# -*- coding: utf-8 -*-
import trainline

results = trainline.search(
	departure_station="Toulouse",
	arrival_station="Bordeaux",
	from_date="15/10/2018 08:00",
	to_date="15/10/2018 21:00")

print(results.csv())
```

Example output :

```bash
departure_date;arrival_date;duration;number_of_segments;price;currency
15/10/2018 08:49;15/10/2018 10:58;02h09;1;15,00;EUR
15/10/2018 10:19;15/10/2018 12:26;02h07;1;17,00;EUR
[...]
```

```python
# -*- coding: utf-8 -*-
import trainline

Pierre = trainline.Passenger(birthdate="01/01/1980")
Sophie = trainline.Passenger(birthdate="01/02/1981")
Enzo = trainline.Passenger(birthdate="01/03/2012", card=trainline.ENFANT_PLUS)

results = trainline.search(
	passengers=[Pierre, Sophie, Enzo],
	departure_station="Toulouse",
	arrival_station="Bordeaux",
	from_date="15/10/2018 08:00",
	to_date="15/10/2018 21:00",
	bicyle_required=True)

print(results.csv())
```

Example output :

```bash
departure_date;arrival_date;duration;number_of_segments;price;currency
15/10/2018 08:49;15/10/2018 10:58;02h09;1;55,00;EUR
15/10/2018 10:19;15/10/2018 12:26;02h07;1;57,00;EUR
[...]
```
