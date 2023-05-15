"""
TPT module
"""
import os
import configparser
import logging
from logging.handlers import RotatingFileHandler
from .file_manager import TPTFileManager
from .extractor import TPTExtractor
from .event import event as evt
from .processor import TPTProcessor
from .comparator import TPTComparator
from .concatenator import TPTConcatenator
from .database import DBAccess
from .activity import Activity
from .learner import Learner
from .request import Request
from .task import Task
from .statistics import TPTStatisticsHelper


class TPT:
    """
    TPT class
    """
    _data = None

    def __init__(self, engine, settings_file='tpt.ini', logger=None, create_db=False, debug=False):
        # Settings object
        self.settings = configparser.ConfigParser()
        self.settings.read(settings_file)
        self.settings._interpolation = configparser.ExtendedInterpolation()

        logs_folder = os.getenv('LOGS_FOLDER', '.')

        # Store the logging object that will be used by all the TPT classes
        if logger is None:
            logger = logging.getLogger("tpt")
            logger.setLevel(logging.INFO)
            if debug is True:
                logger.setLevel(logging.DEBUG)

            log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            if debug is True:
                ch.setLevel(logging.DEBUG)
            ch.setFormatter(log_format)
            logger.addHandler(ch)

            # add a rotating handler
            fh = RotatingFileHandler(logs_folder + '/logfile.log', maxBytes=20000000,
                                     backupCount=5)
            fh.setFormatter(log_format)

            fh.setLevel(logging.INFO)
            if debug is True:
                fh.setLevel(logging.DEBUG)
            logger.addHandler(fh)

        # Store the file manager object that will be used by all the TPT classes
        file_mngr = TPTFileManager(logger, self.settings)

        # Store the data access object that will be used by all the TPT classes
        self._data = DBAccess(engine=engine, log=logger, create_db=create_db)

        # Configure the especialized objects
        extractor = TPTExtractor(file_mngr, self._data, logger, self.settings)
        processor = TPTProcessor(file_mngr, self._data, logger, self.settings)
        concatenator = TPTConcatenator(file_mngr, self._data, logger, self.settings)
        comparator = TPTComparator(file_mngr, self._data, logger, self.settings)

        # Register the events
        self.events = {
            'onStartExtraction': evt.EventHandler(evt.Event("Extraction started"), self),
            'onEndExtraction': evt.EventHandler(evt.Event("Extraction done"), self),
            'onStartAnalysis': evt.EventHandler(evt.Event("Analysis started"), self),
            'onAnalysisPrepared': evt.EventHandler(evt.Event("Analysis prepared"), self),
            'onEndAnalysis': evt.EventHandler(evt.Event("Analysis done"), self),
            'onNewRequest': evt.EventHandler(evt.Event("New request received"), self),
            'onRequestValid': evt.EventHandler(evt.Event("New request is valid"), self),
            'onRequestError': evt.EventHandler(evt.Event("New request is not valid"), self),
            'onNoRequestPrepared': evt.EventHandler(
                evt.Event("There are no prepared requests to analyse"), self)}

        # create properties
        self._activity = Activity(data=self._data, log=logger, file_mngr=file_mngr,
                                  extractor=extractor, concatenator=concatenator)
        self._learner = Learner(data=self._data, file_mngr=file_mngr)
        self._request = Request(data=self._data, events=self.events, log=logger,
                                processor=processor, comparator=comparator, file_mngr=file_mngr)
        self._task = Task(data=self._data, comparator=comparator, processor=processor,
                          extractor=extractor, request=self._request, log=logger,
                          events=self.events)
        self._statistics = TPTStatisticsHelper(data=self._data, settings=self.settings)

    def __del__(self):
        if self._data is not None:
            self._data.close_session()

    @property
    def activity(self):
        """
        Get activity
        :return:
        """
        return self._activity

    @property
    def learner(self):
        """
        Get learner
        :return:
        """
        return self._learner

    @property
    def request(self):
        """
        Get request
        :return:
        """
        return self._request

    @property
    def task(self):
        """
        Get task
        :return:
        """
        return self._task

    @property
    def statistics(self):
        """
        Get statistics
        :return:
        """
        return self._statistics

    def set_config_file(self, file):
        """
        Set config file
        :param file:
        :return:
        """
        self.settings.read(file)
