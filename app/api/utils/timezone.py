# -*- coding: utf-8 -*-
import datetime

class UTC8TZInfo(datetime.tzinfo):
    """Fixed offset in hours east from UTC.
    
    This is a slight adaptation of the ``FixedOffset`` example found in
    https://docs.python.org/2.7/library/datetime.html.
    """
    
    def __init__(self, hours, name):
        self.__offset = datetime.timedelta(hours=hours)
        self.__name = name
    
    def utcoffset(self, dt):
        return self.__offset
    
    def tzname(self, dt):
        return self.__name
    
    def dst(self, dt):
        return datetime.timedelta()


utc8_tzinfo = UTC8TZInfo(hours=8, name="UTC +8")
