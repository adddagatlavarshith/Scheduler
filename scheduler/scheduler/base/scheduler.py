

import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterable
from functools import wraps
from logging import Logger, getLogger
from typing import Any, Callable, Generic, List, Optional, TypeVar

from scheduler.base.job import BaseJobType
from scheduler.base.timingtype import (
    TimingCyclic,
    TimingDailyUnion,
    TimingOnceUnion,
    TimingWeeklyUnion,
)




LOGGER = getLogger("scheduler")


def select_jobs_by_tag(
    jobs: set[BaseJobType],
    tags: set[str],
    any_tag: bool,
) -> set[BaseJobType]:

    if any_tag:
        return {job for job in jobs if tags & job.tags}
    return {job for job in jobs if tags <= job.tags}


def deprecated(fields: List[str]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:


    def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def real_wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Any:
            for f in fields:
                if f in kwargs and kwargs[f] is not None:
                    # keep it in kwargs
                    warnings.warn(
                        (
                            f"Using the `{f}` argument is deprecated and will "
                            "be removed in the next minor release."
                        ),
                        DeprecationWarning,
                        stacklevel=3,
                    )
            return func(*args, **kwargs)

        return real_wrapper

    return wrapper


T = TypeVar("T", bound=Callable[[], Any])


class BaseScheduler(
    ABC, Generic[BaseJobType, T]
):

    _logger: Logger

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._logger = logger if logger else LOGGER

    @abstractmethod
    def delete_job(self, job: BaseJobType) -> None:
        """Delete a |BaseJob| from the `BaseScheduler`."""

    @abstractmethod
    def delete_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> int:
        r"""Delete a set of |BaseJob|\ s from the `BaseScheduler` by tags."""

    @abstractmethod
    def get_jobs(
        self,
        tags: Optional[set[str]] = None,
        any_tag: bool = False,
    ) -> set[BaseJobType]:
        r"""Get a set of |BaseJob|\ s from the `BaseScheduler` by tags."""

    @abstractmethod
    def cyclic(self, timing: TimingCyclic, handle: T, **kwargs) -> BaseJobType:
        """Schedule a cyclic |BaseJob|."""

    @abstractmethod
    def minutely(self, timing: TimingDailyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule a minutely |BaseJob|."""

    @abstractmethod
    def hourly(self, timing: TimingDailyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule an hourly |BaseJob|."""

    @abstractmethod
    def daily(self, timing: TimingDailyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule a daily |BaseJob|."""

    @abstractmethod
    def weekly(self, timing: TimingWeeklyUnion, handle: T, **kwargs) -> BaseJobType:
        """Schedule a weekly |BaseJob|."""

    @abstractmethod
    def once(
        self,
        timing: TimingOnceUnion,
        handle: T,
        *,
        args: Optional[tuple[Any]] = None,
        kwargs: Optional[dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
        alias: Optional[str] = None,
    ) -> BaseJobType:
        """Schedule a oneshot |BaseJob|."""

    @property
    @abstractmethod
    def jobs(self) -> set[BaseJobType]:
        r"""Get the set of all |BaseJob|\ s."""
