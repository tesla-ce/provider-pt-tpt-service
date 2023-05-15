"""
Learner module
"""


class Learner:
    """
    Learner class
    """
    def __init__(self, data, file_mngr):
        self.data = data
        self.file_mngr = file_mngr

    def get_results(self, user_id):
        """
        Get user results
        :param user_id:
        :return:
        """
        # TODO: implement self.data.get_user_results()
        user_results = self.data.get_user_results(user_id)

        return user_results

    def delete_data(self, user_id):
        """
        Delete user data
        :param user_id:
        :return:
        """

        # delete files
        activities = self.data.get_activities_with_requests_from_user_id(user_id)
        for activity_id in activities:
            self.file_mngr.delete_folders_for_activity_and_user_id(activity_id, user_id)

        # delete database data
        requests_affected = self.data.delete_by_user_id(user_id)

        # how can this interfere with current processing tasks for that user???
        # update results????????? of other requests that may be changed after the deletion
        # of the user?

        for request_id in requests_affected:
            request = self.data.get_request(request_id)
            new_score = self.data.recalc_request_score(request_id)
            request.concat_result = new_score
            request.pending_update = True
            self.data.update_request(request)
