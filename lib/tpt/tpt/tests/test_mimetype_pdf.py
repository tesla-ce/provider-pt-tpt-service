from .util_helper import UtilHelper


class TestMimetypePDF(UtilHelper):
    def on_end_analysis(self, request):
        self.test_result_on_end_analysis = request

    def on_end_extraction(self, request):
        self.test_result_on_end_extraction = request

        self.test_result_on_end_extraction = {
            'id': request.id,
            'status': request.status,
            'files_size': request.files_size
        }

    def test_send_pdf_ok_result_99(self):
        tpt = self.get_tpt()
        tpt.events['onEndAnalysis'] += self.on_end_analysis
        original_request_id = "1"
        user_id = 1
        activity_id = 3

        data = self.get_sample_b64_from_path('document1_raw.pdf', 'application/pdf')
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()

        original_request_id = "2"
        user_id = 2
        activity_id = 3

        data = self.get_sample_b64_from_path('document2_raw.pdf', 'application/pdf')
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()
        tpt.task.update.execute()

        while self.test_result_on_end_analysis is None:
            pass

        self.assertEqual(self.test_result_on_end_analysis['request_id'], "1")
        self.assertAlmostEqual(self.test_result_on_end_analysis['result'], 99, delta=1)
        aux_audit = self.test_result_on_end_analysis['audit_data']

        for concat in aux_audit:
            self.assertEqual(concat['concat_a_concat_id'], 1)
            self.assertEqual(concat['concat_b_concat_id'], 1)
            self.assertEqual(concat['tesla_id'], '2')
            self.assertAlmostEqual(concat['result'], 0.99, delta=0.2)
            self.assertEqual(concat['type'], 'TEXT_ONLY')

    def test_send_pdf_ok_result_0(self):
        tpt = self.get_tpt()
        tpt.events['onEndAnalysis'] += self.on_end_analysis
        original_request_id = "1"
        user_id = 1
        activity_id = 4

        data = self.get_sample_b64_from_path('document1_raw.pdf', 'application/pdf')
        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()

        original_request_id = 2
        user_id = 2
        activity_id = 4

        data = self.get_sample_b64_from_path('document2.pdf', 'application/pdf')
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
