"""
Implementation of the essential timer for a `BaseJob`.


"""

from __future__ import annotations

import datetime as dt
import threading
from typing import Optional, cast

from scheduler.base.definition import JobType
from scheduler.base.timingtype import TimingJobTimerUnion
from scheduler.trigger.core import Weekday
from scheduler.util import JOB_NEXT_DAYLIKE_MAPPING, next_weekday_time_occurrence


class JobTimer:


    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobTimerUnion,
        start: dt.datetime,
        skip_missing: bool = False,
    ):
        self.__lock = threading.RLock()
        self.__job_type = job_type
        self.__timing = timing
        self.__next_exec = start
        self.__skip = skip_missing
        self.calc_next_exec()

    def calc_next_exec(self, ref: Optional[dt.datetime] = None) -> None:

        with self.__lock:
            if self.__job_type == JobType.CYCLIC:
                if self.__skip and ref is not None:
                    self.__next_exec = ref
                self.__next_exec = self.__next_exec + cast(dt.timedelta, self.__timing)
                return

            if self.__job_type == JobType.WEEKLY:
                self.__timing = cast(Weekday, self.__timing)
                if self.__timing.time.tzinfo:
                    self.__next_exec = self.__next_exec.astimezone(self.__timing.time.tzinfo)
                self.__next_exec = next_weekday_time_occurrence(
                    self.__next_exec, self.__timing, self.__timing.time
                )

            else:  # self.__job_type in JOB_NEXT_DAYLIKE_MAPPING:
                self.__timing = cast(dt.time, self.__timing)
                if self.__next_exec.tzinfo:
                    self.__next_exec = self.__next_exec.astimezone(self.__timing.tzinfo)
                self.__next_exec = JOB_NEXT_DAYLIKE_MAPPING[self.__job_type](
                    self.__next_exec, self.__timing
                )

            if self.__skip and ref is not None and self.__next_exec < ref:
                self.__next_exec = ref
                self.calc_next_exec()

    @property
    def datetime(self) -> dt.datetime:

        with self.__lock:
            return self.__next_exec

    def timedelta(self, dt_stamp: dt.datetime) -> dt.timedelta:

        with self.__lock:
            return self.__next_exec - dt_stamp
