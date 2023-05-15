"""
Event module
"""
from .event_handler import EventHandler


class Event:
    """
    Event class
    """
    def __init__(self, doc=None):
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return EventHandler(self, obj)

    def __set__(self, obj, value):
        pass
