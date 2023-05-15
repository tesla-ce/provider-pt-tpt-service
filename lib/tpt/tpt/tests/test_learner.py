import pytest
from .util_helper import UtilHelper


class TestLearner(UtilHelper):
    @pytest.mark.skip(reason="TODO: Implement first tpt.learner.get_results() function")
    @pytest.mark.xfail(reason="TODO: Implement first tpt.learner.get_results() function")
    def test_get_results(self):
        # TODO: Implement first tpt.learner.get_results() function
        
        tpt = self.get_tpt()

        original_request_id = 1
        user_id = 1
        activity_id = 1

        mimetype = 'plain/text'
        data = self.get_sample_b64_from_path('moodle_file15.txt', mimetype)
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute(request_id, data)
        tpt.task.process.execute(request_id=request_id)
        tpt.task.compare.execute()

        results = tpt.learner.get_results(user_id=user_id)

    @pytest.mark.xfail(reason="TODO: Implement first tpt.learner.get_results() function")
    def test_delete(self):
        tpt = self.get_tpt()

        original_request_id = 1
        user_id = 1
        activity_id = 1

        mimetype = 'plain/text'
        data = self.get_sample_b64_from_path('moodle_file15.txt', mimetype)
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()

        tpt.learner.delete_data(user_id=user_id)

        # TODO: Implement first tpt.learner.get_results() function
        results = tpt.learner.get_results(user_id=user_id)
