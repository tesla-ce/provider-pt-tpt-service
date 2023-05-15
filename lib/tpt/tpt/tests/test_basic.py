import base64
from .util_helper import UtilHelper
from tpt.commons import ReqStatusEnum


class TestBasic(UtilHelper):
    test_result_on_end_analysis = None
    test_result_on_end_extraction = None

    def on_end_analysis(self, request):
        self.test_result_on_end_analysis = request

    def on_end_extraction(self, request):
        self.test_result_on_end_extraction = request

        self.test_result_on_end_extraction = {
            'id': request.id,
            'status': request.status,
            'files_size': request.files_size
        }

    def test_send_plain_text_data_ok(self):
        tpt = self.get_tpt()
        tpt.events['onEndAnalysis'] += self.on_end_analysis
        original_request_id = "1"
        user_id = 1
        activity_id = '1'

        # format: filename:<file>,data:<mime_type>;base64,<data64>
        data = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. " \
               "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, " \
               "when an unknown printer took a galley of type and scrambled it to make a type " \
               "specimen book. It has survived not only five centuries, but also the leap into " \
               "electronic typesetting, remaining essentially unchanged. It was popularised in " \
               "the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, " \
               "and more recently with desktop publishing software like Aldus PageMaker " \
               "including versions of Lorem Ipsum"
        data_b64 = base64.b64encode(data.encode('utf8'))
        data = self.get_sample_b64_from_content(data_b64, 'plain/text', 'lorem.txt')

        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()

        original_request_id = "2"
        user_id = 2
        activity_id = 1

        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)

        tpt.task.extract.execute()
        tpt.task.compare.execute()
        tpt.task.update.execute()

        while self.test_result_on_end_analysis is None:
            pass

        self.assertEqual(self.test_result_on_end_analysis['request_id'], "1")
        self.assertEqual(self.test_result_on_end_analysis['result'], 100.0)
        aux_audit = self.test_result_on_end_analysis['audit_data']

        for concat in aux_audit:
            self.assertEqual(concat['concat_a_concat_id'], 1)
            self.assertEqual(concat['concat_b_concat_id'], 1)
            self.assertEqual(concat['tesla_id'], '2')
            self.assertEqual(concat['result'], 1.0)
            self.assertEqual(concat['type'], 'TEXT_ONLY')

    def test_send_plain_text_data_empty(self):
        tpt = self.get_tpt()
        tpt.events['onEndExtraction'] += self.on_end_extraction
        tpt.events['onEndAnalysis'] += self.on_end_analysis
        original_request_id = 3
        user_id = 1
        activity_id = 1

        # format: filename:<file>,data:<mime_type>;base64,<data64>
        data_b64 = base64.b64encode("".encode('utf8'))
        data = self.get_sample_b64_from_content(data_b64, 'plain/text', 'lorem.txt')

        request_id = tpt.task.prepare.execute(original_request_id, user_id, activity_id, data)
        tpt.task.extract.execute()
        tpt.task.compare.execute()

        while self.test_result_on_end_extraction is None:
            pass

        self.assertEqual(self.test_result_on_end_extraction['id'], 1)
        self.assertEqual(self.test_result_on_end_extraction['status'], ReqStatusEnum.ERROR)
        self.assertEqual(self.test_result_on_end_extraction['files_size'], 0)
