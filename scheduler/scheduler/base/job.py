

from __future__ import annotations

import datetime as dt
import warnings
from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Callable, Generic, Optional, TypeVar, cast

from scheduler.base.definition import JobType
from scheduler.base.job_timer import JobTimer
from scheduler.base.job_util import (
    check_duplicate_effective_timings,
    check_timing_tzinfo,
    get_pending_timer,
    prettify_timedelta,
    sane_timing_types,
    set_start_check_stop_tzinfo,
    standardize_timing_format,
)
from scheduler.base.timingtype import TimingJobUnion

T = TypeVar("T", bound=Callable[[], Any])


class BaseJob(ABC, Generic[T]):
    """Abstract definition basic interface for a job class."""

    __type: JobType
    __timing: TimingJobUnion
    __handle: T
    __args: tuple[Any, ...]
    __kwargs: dict[str, Any]
    __max_attempts: int
    __tags: set[str]
    __delay: bool
    __start: Optional[dt.datetime]
    __stop: Optional[dt.datetime]
    __skip_missing: bool
    __alias: Optional[str]
    __tzinfo: Optional[dt.tzinfo]
    __logger: Logger

    __mark_delete: bool
    __attempts: int
    __failed_attempts: int
    __pending_timer: JobTimer
    __timers: list[JobTimer]

    def __init__(
        self,
        job_type: JobType,
        timing: TimingJobUnion,
        handle: T,
        *,
        args: Optional[tuple[Any, ...]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        max_attempts: int = 0,
        tags: Optional[set[str]] = None,
        delay: bool = True,
        start: Optional[dt.datetime] = None,
        stop: Optional[dt.datetime] = None,
        skip_missing: bool = False,
        alias: Optional[str] = None,
        tzinfo: Optional[dt.tzinfo] = None,
    ):
        timing = standardize_timing_format(job_type, timing)

        sane_timing_types(job_type, timing)
        check_timing_tzinfo(job_type, timing, tzinfo)
        check_duplicate_effective_timings(job_type, timing, tzinfo)

        self.__start = set_start_check_stop_tzinfo(start, stop, tzinfo)

        self.__type = job_type
        self.__timing = timing  # pylint: disable=unused-private-member

        self.__handle = handle
        self.__args = () if args is None else args
        self.__kwargs = {} if kwargs is None else kwargs.copy()
        self.__max_attempts = max_attempts
        self.__tags = set() if tags is None else tags.copy()
        self.__delay = delay
        self.__stop = stop
        self.__skip_missing = skip_missing
        self.__alias = alias
        self.__tzinfo = tzinfo

        # self.__mark_delete will be set to True if the new Timer would be in future
        # relativ to the self.__stop variable
        self.__mark_delete = False
        self.__attempts = 0
        self.__failed_attempts = 0

        # create JobTimers
        self.__timers = [JobTimer(job_type, tim, self.__start, skip_missing) for tim in timing]
        self.__pending_timer = get_pending_timer(self.__timers)

        if self.__stop is not None:
            if self.__pending_timer.datetime > self.__stop:
                self.__mark_delete = True

    def __lt__(self, other: BaseJob[T]) -> bool:
        return self.datetime < other.datetime

    def _calc_next_exec(self, ref_dt: dt.datetime) -> None:

        if self.__skip_missing:
            for timer in self.__timers:
                if (timer.datetime - ref_dt).total_seconds() <= 0:
                    timer.calc_next_exec(ref_dt)
        else:
            self.__pending_timer.calc_next_exec(ref_dt)
        self.__pending_timer = get_pending_timer(self.__timers)
        if self.__stop is not None and self.__pending_timer.datetime > self.__stop:
            self.__mark_delete = True

    def _repr(self) -> tuple[str, ...]:
        return tuple(
            repr(elem)
            for elem in (
                self.__type,
                self.__timing,
                self.__handle,
                self.__args,
                self.__kwargs,
                self.__max_attempts,
                self.__delay,
                self.__start,
                self.__stop,
                self.__skip_missing,
                self.__alias,
                self.tzinfo,
            )
        )

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError()  # pragma: no cover

    def _str(
        self,
    ) -> tuple[str, ...]:
        """Return the objects relevant for readable string representation."""
        dt_timedelta = self.timedelta(dt.datetime.now(self.tzinfo))
        if self.alias is not None:
            f_args = ""
        elif hasattr(self.handle, "__code__"):
            f_args = "(..)" if self.handle.__code__.co_nlocals else "()"
        else:
            f_args = "(?)"
        return (
            self.type.name if self.max_attempts != 1 else "ONCE",
            self.handle.__qualname__ if self.alias is None else self.alias,
            f_args,
            str(self.datetime)[:19],
            str(self.datetime.tzname()),
            prettify_timedelta(dt_timedelta),
            str(self.attempts),
            str(float("inf") if self.max_attempts == 0 else self.max_attempts),
        )

    def __str__(self) -> str:
        return "{0}, {1}{2}, at={3}, tz={4}, in={5}, #{6}/{7}".format(*self._str())

    def timedelta(self, dt_stamp: Optional[dt.datetime] = None) -> dt.timedelta:

        if dt_stamp is None:
            dt_stamp = dt.datetime.now(self.__tzinfo)
        if not self.__delay and self.__attempts == 0:
            return cast(dt.datetime, self.__start) - dt_stamp
        return self.__pending_timer.timedelta(dt_stamp)

    @property
    def datetime(self) -> dt.datetime:

        if not self.__delay and self.__attempts == 0:
            return cast(dt.datetime, self.__start)
        return self.__pending_timer.datetime

    @property
    def type(self) -> JobType:

        return self.__type

    @property
    def handle(self) -> T:
        """
        Get the callback function.

        Returns
        -------
        handle
            Callback function.
        """
        return self.__handle

    @property
    def args(self) -> tuple[Any, ...]:

        return self.__args

    @property
    def kwargs(self) -> dict[str, Any]:

        return self.__kwargs

    @property
    def max_attempts(self) -> int:

        return self.__max_attempts

    @property
    def tags(self) -> set[str]:

        return self.__tags.copy()

    @property
    def delay(self) -> bool:

        warnings.warn(
            (
                "Using the `delay` property is deprecated and will "
                "be removed in the next minor release."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        return self.__delay

    @property
    def start(self) -> Optional[dt.datetime]:

        return self.__start

    @property
    def stop(self) -> Optional[dt.datetime]:

        return self.__stop

    @property
    def skip_missing(self) -> bool:

        return self.__skip_missing

    @property
    def alias(self) -> Optional[str]:

        return self.__alias

    @property
    def tzinfo(self) -> Optional[dt.tzinfo]:

        return self.datetime.tzinfo

    @property
    def _tzinfo(self) -> Optional[dt.tzinfo]:

        return self.__tzinfo

    @property
    def attempts(self) -> int:

        return self.__attempts

    @property
    def failed_attempts(self) -> int:

        return self.__failed_attempts

    @property
    def has_attempts_remaining(self) -> bool:

        if self.__mark_delete:
            return False
        if self.__max_attempts == 0:
            return True
        return self.__attempts < self.__max_attempts


BaseJobType = TypeVar("BaseJobType", bound=BaseJob[Any])
