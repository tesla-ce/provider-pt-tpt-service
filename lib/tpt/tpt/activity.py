"""
Activity module
"""
from .commons import CmpTypeEnum, ActContextEnum
from .model import TPTActivity


class Activity:
    """"
    Activity class
    """
    def __init__(self, data, log, file_mngr, extractor, concatenator):
        self.data = data
        self.log = log
        self.file_mngr = file_mngr
        self.extractor = extractor
        self.concatenator = concatenator

    def set_config(self, activity_id, course_id=None, start_date=None, end_date=None,
                            activity_type=CmpTypeEnum.TEXT,
                            context=ActContextEnum.ACTIVITY, config=None):
        """
        Set activity config
        :param activity_id:
        :param course_id:
        :param start_date:
        :param end_date:
        :param activity_type:
        :param context:
        :param config:
        :return:
        """
        activity = TPTActivity(activity_id=activity_id, course_id=course_id,
                               start_date=start_date, end_date=end_date,
                               activity_type=activity_type, context=context, config=config)

        self.data.add_or_update_activity(activity)

    def get_config(self, activity_id):
        """
        Get activity config
        :param activity_id:
        :return:
        """
        activity_id = str(activity_id)
        activity = self.data.get_activity(activity_id)
        if activity is not None:
            self.log.debug(activity.config)

        return activity

    def prepare(self, activity_id, course_id=None, start_date=None, end_date=None,
                activity_type=None, context=None, config=None, data=None, path=None):
        """
        Prepare activity

        :param activity_id:
        :param course_id:
        :param start_date:
        :param end_date:
        :param activity_type:
        :param context:
        :param config:
        :param data:
        :param path:
        :return:
        """
        # Create a new activity
        activity = TPTActivity(activity_id=activity_id, course_id=course_id,
                               start_date=start_date, end_date=end_date,
                               activity_type=activity_type, context=context, config=config)

        self.data.add_or_update_activity(activity)
        return
        # Launch the event for start preparing
        # self.onStartExtraction.fire(activity)

        if data is not None:
            # Apply the extractor
            self.extractor.process_statement(activity, data=data, path=path)
            self.concatenator.create_concatenated_statement(activity)

        # Launch the event for start preparing
        # self.onEndExtraction.fire(activity)

    def get_results(self, activity_id):
        """
        Get results
        :param activity_id:
        :return:
        """
        activity_results = self.data.get_activity_results(activity_id)

        return activity_results

    def delete(self, activity_id, recalc_scores=True, delete_requests=True):
        """
        Delete activity
        :param activity_id:
        :param recalc_scores:
        :param delete_requests:
        :return:
        """
        # delete database data
        activity_id = str(activity_id)
        requests_affected = self.data.delete_by_activity_id(activity_id=activity_id,
                                                            delete_requests=delete_requests)
        # how can this interfere with current processing tasks for that user???
        # update results????????? of other requests that may be changed after the deletion
        # of the user?
        if recalc_scores is True:
            for request_id in requests_affected:
                request = self.data.get_request(request_id)

                if request is not None:
                    new_score = self.data.recalc_request_score(request_id)
                    request.concat_result = new_score
                    request.pending_update = True
                    self.data.update_request(request)

        # delete files
        if delete_requests is True:
            self.file_mngr.delete_folders_for_activity(activity_id=activity_id)
            self.data.delete_activity(activity_id)

    def archive_data(self, activity_id):
        """
        Archive activity data, without recalc all scores and delete requests.
        :param activity_id:
        :return:
        """
        self.delete(activity_id=activity_id, recalc_scores=False, delete_requests=False)

    def archive_data(self, activity_id):
        """
        Archive activity data, without recalc all scores and delete requests.
        :param activity_id:
        :return:
        """
        self.delete(activity_id=activity_id, recalc_scores=False, delete_requests=False)