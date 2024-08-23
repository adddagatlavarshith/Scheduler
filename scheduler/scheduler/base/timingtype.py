# in this all the timing types are defined

import datetime as dt
from typing import Union

from scheduler.trigger.core import Weekday

TimingCyclic = dt.timedelta
_TimingCyclicList = list[TimingCyclic]
# time on the clock
_TimingDaily = dt.time