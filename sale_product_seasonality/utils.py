# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime


def roundTimeDT(dt=None, dateDelta=None):
    """Round a datetime object to a multiple of a timedelta

    :param dt: datetime.datetime object, default now.
    :param dateDelta: timedelta object, we round to a multiple of this, default 1 minute.

    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
            Stijn Nevens 2014 - Changed to use only datetime objects as variables
    """
    dateDelta = dateDelta or datetime.timedelta(minutes=1)
    roundTo = dateDelta.total_seconds()

    if dt is None:
        dt = datetime.datetime.now()
    seconds = (dt - dt.min).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds + roundTo / 2) // roundTo * roundTo
    return dt + datetime.timedelta(0, rounding - seconds, -dt.microsecond)


def roundTime(dt=None, hours=0, minutes=0, seconds=0):
    return roundTimeDT(
        dt=dt,
        dateDelta=datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds),
    )
