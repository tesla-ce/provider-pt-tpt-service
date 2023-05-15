"""
Update module
"""


class Update:
    """
    Update task
    """
    def __init__(self, data, log, request):
        self.data = data
        self.log = log
        self.request = request

    def __str__(self):
        return self.__class__.__name__

    def execute(self):
        """
        Recalculate pending results
        :return:
        """
        request = self.data.get_next_pending_update_request()

        if request is not None:
            self.log.debug("UPDATING REQUEST: {}".format(request.original_request_id))
            self.request.update_result(request)
            return True

        return False
