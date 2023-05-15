"""
Task extract module
"""
from tpt.commons import ReqStatusEnum


class Extract:
    """
    Extract class
    """
    def __init__(self, data, extractor, processor, events, log):
        self.data = data
        self.extractor = extractor
        self.processor = processor
        self.events = events
        self.log = log

    def __str__(self):
        return self.__class__.__name__

    def execute(self):
        """
        Extract pending extract requests
        :return:
        """

        requests = self.data.get_pending_extract_requests()

        for request in requests:
            # Launch the event for start preparing
            self.events['onStartExtraction'].fire(request)

            # Apply the extractor
            result = self.extractor.process(request)
            if result is False:
                request.status = ReqStatusEnum.ERROR
                self.data.update_request(request)

            # Launch the event for start preparing
            self.events['onEndExtraction'].fire(request)
            self.processor.process(request)
