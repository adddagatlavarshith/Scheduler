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

class Monday(Weekday):
    __doc__ = Weekday.__doc__

    def __init__(self, time: dt.time = dt.time()) -> None:
        super().__init__(time, 0)


class Tuesday(Weekday):
    __doc__ = Weekday.__doc__

    def __init__(self, time: dt.time = dt.time()) -> None:
        super().__init__(time, 1)


class Wednesday(Weekday):
    __doc__ = Weekday.__doc__

    def __init__(self, time: dt.time = dt.time()) -> None:
        super().__init__(time, 2)


class Thursday(Weekday):
    __doc__ = Weekday.__doc__

    def __init__(self, time: dt.time = dt.time()) -> None:
        super().__init__(time, 3)


class Friday(Weekday):
    __doc__ = Weekday.__doc__

    def __init__(self, time: dt.time = dt.time()) -> None:
        super().__init__(time, 4)


class Saturday(Weekday):
    __doc__ = Weekday.__doc__

    def __init__(self, time: dt.time = dt.time()) -> None:
        super().__init__(time, 5)


class Sunday(Weekday):
    __doc__ = Weekday.__doc__

    def __init__(self, time: dt.time = dt.time()) -> None:
        super().__init__(time, 6)


_Weekday = Union[Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday]

_weekday_mapping: dict[int, type[_Weekday]] = {
    0: Monday,
    1: Tuesday,
    2: Wednesday,
    3: Thursday,
    4: Friday,
    5: Saturday,
    6: Sunday,
}


def weekday(value: int, time: dt.time = dt.time()) -> Weekday:
    """
    Return |Weekday| from given value with optional time.
    """
    weekday_cls: type[_Weekday] = _weekday_mapping[value]
    weekday_instance = weekday_cls(time)
    return weekday_instance


