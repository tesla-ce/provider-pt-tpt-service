from .util_helper import UtilHelper


class TestMimetypeTXT(UtilHelper):
    def on_end_analysis(self, request):
        self.test_result_on_end_analysis = request

    def on_end_extraction(self, request):
        self.test_result_on_end_extraction = request

        self.test_result_on_end_extraction = {
            'id': request.id,
            'status': request.status,
            'files_size': request.files_size
        }

    def test_send_docx_ok_result_0(self):
        tpt = self.get_tpt()
        tpt.events['onEndAnalysis'] += self.on_end_analysis
        original_request_id = 1
        user_id = 1
        activity_id = 5

        mimetype = 'plain/text'
        data = self.get_sample_b64_from_path('moodle_file15.txt', mimetype)
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()

        original_request_id = "2"
        user_id = 2
        activity_id = 5

        data = self.get_sample_b64_from_path('moodle_file32.txt', mimetype)
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()
        tpt.task.update.execute()

        while self.test_result_on_end_analysis is None:
            pass

        self.assertEqual(self.test_result_on_end_analysis['request_id'], "2")
        self.assertEqual(self.test_result_on_end_analysis['result'], 0.0)
        aux_audit = self.test_result_on_end_analysis['audit_data']

        for concat in aux_audit:
            self.assertEqual(concat['concat_a_concat_id'], 1)
            self.assertEqual(concat['concat_b_concat_id'], 1)
            self.assertEqual(concat['tesla_id'], '1')
            self.assertEqual(concat['result'], 0.0)
            self.assertEqual(concat['type'], 'TEXT_ONLY')

    def test_send_docx_ok_result_4(self):
        tpt = self.get_tpt()
        tpt.events['onEndAnalysis'] += self.on_end_analysis
        original_request_id = 1
        user_id = 1
        activity_id = 6

        mimetype = 'plain/text'
        data = self.get_sample_b64_from_path('moodle_file15.txt', mimetype)
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()

        original_request_id = "2"
        user_id = 2
        activity_id = 6

        data = self.get_sample_b64_from_path('moodle_file32_mod.txt', mimetype)
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()
        tpt.task.update.execute()

        while self.test_result_on_end_analysis is None:
            pass

        self.assertEqual(self.test_result_on_end_analysis['request_id'], "1")
        self.assertEqual(self.test_result_on_end_analysis['result'], 4.0)
        aux_audit = self.test_result_on_end_analysis['audit_data']

        for concat in aux_audit:
            self.assertEqual(concat['concat_a_concat_id'], 1)
            self.assertEqual(concat['concat_b_concat_id'], 1)
            self.assertEqual(concat['tesla_id'], '2')
            self.assertEqual(concat['result'], 0.04)
            self.assertEqual(concat['type'], 'TEXT_ONLY')
