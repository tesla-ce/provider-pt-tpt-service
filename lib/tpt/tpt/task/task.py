"""
Task module
"""
from .analyze import Analyze
from .compare import Compare
from .extract import Extract
from .prepare import Prepare
from .update import Update


class Task:
    """
    Task class
    """
    def __init__(self, data, comparator, processor, extractor, request, log, events):
        self._analyze = Analyze(data=data, processor=processor, comparator=comparator, log=log,
                                events=events)
        self._compare = Compare(data=data, comparator=comparator, log=log)
        self._prepare = Prepare(data=data, extractor=extractor, events=events, log=log)
        self._update = Update(data=data, log=log, request=request)
        self._extract = Extract(data=data, extractor=extractor, events=events, processor=processor,
                                log=log)

    @property
    def analyze(self):
        """
        Analyzer
        :return:
        """
        return self._analyze

    @property
    def compare(self):
        """
        Comparer
        :return:
        """
        return self._compare

    @property
    def prepare(self):
        """
        Preparer
        :return:
        """
        return self._prepare

    @property
    def update(self):
        """
        Updater
        :return:
        """
        return self._update

    @property
    def extract(self):
        """
        Extractor
        :return:
        """
        return self._extract
