"""
Trigger implementations.

"""

import datetime as dt
from abc import ABC, abstractmethod
from typing import Union


class Weekday(ABC):
    """
    |Weekday| object with time.

    Parameters
    ----------
    time : datetime.time
        Time on the clock at the specific |Weekday|.
    """

    __value: int
    __time: dt.time

    @abstractmethod
    def __init__(self, time: dt.time, value: int) -> None:
        """|Weekday| object with time."""
        self.__time = time
        self.__value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(time={self.time!r})"

    @property
    def time(self) -> dt.time:
        """
        Return time of the |Weekday|.

        Returns
        -------
        datetime.time
            Time on the clock at the specific |Weekday|.
        """
        return self.__time

    @property
    def value(self) -> int:
        """
        Return value of the given |Weekday|.

        Notes
        -----
        Enumeration analogous to datetime library (0: Monday, ... 6: Sunday).

        Returns
        -------
        int
            Value
        """
        return self.__value



