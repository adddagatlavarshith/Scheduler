"""
Collection of datetime and trigger related utility functions.


"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from scheduler.base.definition import JobType
from scheduler.error import SchedulerError
from scheduler.trigger.core import Weekday


def days_to_weekday(wkdy_src: int, wkdy_dest: int) -> int:

    if not (0 <= wkdy_src <= 6 and 0 <= wkdy_dest <= 6):
        raise SchedulerError("Weekday enumeration interval: [0,6] <=> [Monday, Sunday]")

    return (wkdy_dest - wkdy_src - 1) % 7 + 1


def next_daily_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:

    target = now.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    if (target - now).total_seconds() <= 0:
        target = target + dt.timedelta(days=1)
    return target


def next_hourly_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:

    target = now.replace(
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    if (target - now).total_seconds() <= 0:
        target = target + dt.timedelta(hours=1)
    return target


def next_minutely_occurrence(now: dt.datetime, target_time: dt.time) -> dt.datetime:

    target = now.replace(
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    if (target - now).total_seconds() <= 0:
        return target + dt.timedelta(minutes=1)
    return target


def next_weekday_time_occurrence(
    now: dt.datetime, weekday: Weekday, target_time: dt.time
) -> dt.datetime:

    days = days_to_weekday(now.weekday(), weekday.value)
    if days == 7:
        candidate = next_daily_occurrence(now, target_time)
        if candidate.date() == now.date():
            return candidate

    delta = dt.timedelta(days=days)
    target = now.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=target_time.microsecond,
    )
    return target + delta


JOB_NEXT_DAYLIKE_MAPPING = {
    JobType.MINUTELY: next_minutely_occurrence,
    JobType.HOURLY: next_hourly_occurrence,
    JobType.DAILY: next_daily_occurrence,
}


def are_times_unique(
    timelist: list[dt.time],
) -> bool:

    ref = dt.datetime(year=1970, month=1, day=1)
    collection = {
        ref.replace(
            hour=time.hour,
            minute=time.minute,
            second=time.second,
            microsecond=time.microsecond,
        )
        + (time.utcoffset() or dt.timedelta())
        for time in timelist
    }
    return len(collection) == len(timelist)


def are_weekday_times_unique(weekday_list: list[Weekday], tzinfo: Optional[dt.tzinfo]) -> bool:

    ref = dt.datetime(year=1970, month=1, day=1, tzinfo=tzinfo)
    collection = {
        next_weekday_time_occurrence(ref.astimezone(day.time.tzinfo), day, day.time)
        for day in weekday_list
    }
    return len(collection) == len(weekday_list)
