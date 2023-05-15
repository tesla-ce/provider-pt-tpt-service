"""
Task analyze module
"""
from tpt.commons import ReqCmpJobTypeEnum, ReqStatusEnum, TPTException


class Analyze:
    """
    Task analyze class
    """
    def __init__(self, data, processor, comparator, log, events):
        self.data = data
        self.processor = processor
        self.comparator = comparator
        self.log = log
        self.events = events

    def __str__(self):
        return self.__class__.__name__

    def execute(self):
        """
        Analyze request
        """
        request = None

        try:
            # Obtain a pending request
            request = self.data.get_prepared_request()

            # Launch the event in case of no requests prepared
            if request is None:
                self.events.onNoRequestPrepared.fire(None)
                return False

            self.log.debug("ANALYZING REQUEST " + str(request.originalrequestid))

            # Launch the event for start processing
            self.events.onStartAnalysis.fire(request)

            # Process the request
            count = self.processor.process(request, ReqCmpJobTypeEnum.CONCATS)

            if count == 0:

                # No comparisons have to be done, so update with 0 score and fire update event
                if self.comparator.update_request_result(request, 0, type):
                    request.status = ReqStatusEnum.PROCESSED
                    request.pending_update = True
                    self.data.update_request(request)
                    self.log.info('set pending_update True for request {}'.
                                  format(request.originalrequestid))

            self.events.onAnalysisPrepared.fire(request)

        except Exception as err:
            self.log.exception(err)

            if request is not None:
                request.status = ReqStatusEnum.ERROR
                self.data.update_request(request)

            raise TPTException from err

        return True
