"""
Task prepare module
"""
from tpt.commons import TPTException, ReqStatusEnum
from tpt.model import TPTActivity, TPTRequest


class Prepare:
    """
    Prepare class
    """
    def __init__(self, data, extractor, events, log):
        self.data = data
        self.extractor = extractor
        self.events = events
        self.log = log

    def __str__(self):
        return self.__class__.__name__

    def execute(self, original_request_id, user_id, activity_id, data=None):
        """
        Prepare request
        :param original_request_id:
        :param user_id:
        :param activity_id:
        :param data:
        :param path:
        :return:
        """
        if data is None:
            raise TPTException("Invalid request. The file or the raw data must be provided")

        activity_id = str(activity_id)
        activity = self.data.get_activity(activity_id)

        if activity is None:
            activity = TPTActivity(activity_id=activity_id)
            self.data.add_or_update_activity(activity)

        # Create a new request
        req = TPTRequest(original_request_id=original_request_id, user_id=user_id,
                         activity_id=activity.activity_id, path=None)
        req.status = ReqStatusEnum.PENDING_EXTRACT
        req = self.data.add_or_update_request(req)

        req.path = self.extractor.save_data_request(req, data)
        self.data.add_or_update_request(req)

        return req.id
