#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CLI tool for trainline."""
import click
import trainline
from datetime import datetime, timedelta

# Usage : trainline_cli.py --help


@click.command()
@click.option(
    '--departure', '-d',
    envvar="PARAM1",
    type=str,
    help='departure station (example : Toulouse)',
    required=True,
)
@click.option(
    '--arrival', '-a',
    type=str,
    help='arrival station (example : Bordeaux)',
    required=True,
)
@click.option(
    '--next', '-n',
    type=str,
    help='period of search from now \
(example : 1day, 2days, 3d, 1hour, 2hours, 3h)',
    default='3hours',
    show_default=True,
)
@click.option(
    '--transport', '-t',
    type=click.Choice(['train', 'coach', 'any']),
    help='get only results for the selected transportation mean',
    default='train',
    show_default=True,
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='verbose mode',
)
def main(departure, arrival, next, transport, verbose):
    """ Search trips with Trainline and returns it in csv """

    # Get current datetime > from_date
    from_date_obj = datetime.now()

    # Decode duration (ex : 1day => timedelta(days=1))
    delta = _decode_next_param(next)

    # Calculate the end date > to_date
    to_date_obj = from_date_obj + delta

    # Convert the datetime objects to strings
    from_date = from_date_obj.strftime("%d/%m/%Y %H:%M")
    to_date = to_date_obj.strftime("%d/%m/%Y %H:%M")

    if transport == "any":
        transport = None

    if verbose:
        print()
        print("Search trips from {} to {}, between {} and {}\n".format(
            departure, arrival, from_date, to_date))

    results = trainline.search(
        departure_station=departure,
        arrival_station=arrival,
        from_date=from_date,
        to_date=to_date,
        transportation_mean=transport)

    print(results.csv())

    if verbose:
        print()
        print("{} results".format(len(results)))


def _decode_next_param(next_param):
        """ From a 'next' string, returns a timedelta object
        >>> print(_decode_next_param("1day"))
        1 day, 0:00:00
        >>> print(_decode_next_param("2d"))
        2 days, 0:00:00
        >>> print(_decode_next_param("3hours"))
        3:00:00
        >>> print(_decode_next_param("4h"))
        4:00:00
        """
        if "d" in next_param:
            delta = timedelta(days=int(next_param.split("d")[0]))
        elif "h" in next_param:
            delta = timedelta(hours=int(next_param.split("h")[0]))
        else:
            delta = timedelta(hours=3)
        return delta

if __name__ == "__main__":
    main()
