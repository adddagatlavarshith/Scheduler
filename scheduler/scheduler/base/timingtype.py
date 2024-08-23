# in this all the timing types are defined

import datetime as dt
from typing import Union

from scheduler.trigger.core import Weekday

TimingCyclic = dt.timedelta
_TimingCyclicList = list[TimingCyclic]
# time on the clock
_TimingDaily = dt.time
TimingDailyList = list[_TimingDaily]  # Job
TimingDailyUnion = Union[_TimingDaily, _TimingDailyList]

TimingWeekly = Weekday
_TimingWeeklyList = list[_TimingWeekly]
TimingWeeklyUnion = Union[_TimingWeekly, _TimingWeeklyList]