"""
Request module
"""
import codecs
from .commons import ReqStatusEnum
from .model import TPTFile


class Request:
    """
    Request class
    """
    def __init__(self, data, events, log, processor, comparator, file_mngr):
        self.data = data
        self.events = events
        self.log = log
        self.processor = processor
        self.comparator = comparator
        self.file_mngr = file_mngr

    def update_result(self, req):
        """
        Update request result
        :param req:
        :return:
        """
        self.log.debug('updating request {}'.format(req.original_request_id))

        result = req.files_result

        if result is None or req.concats_result > result:
            result = req.concats_result
            self.log.debug('UPDATING REQUEST RESULT')

        # Launch the event for end processing
        self.events['onEndAnalysis'].fire({'request_id': req.original_request_id, 'result': result,
                                        'audit_data': self.get_audit_data(req.original_request_id)})

        req.pending_update = False
        req.status = ReqStatusEnum.PROCESSED

        self.data.update_request(req)
        # self.data.close_session()

    def get_audit_data(self, original_request_id):
        """
        Get audit data
        :param original_request_id:
        :return:
        """
        comparisons = []

        # get the request
        request = self.data.get_request_by_original_request_id(original_request_id)

        if request is not None:
            # get the request comparisons
            comparisons = self.data.get_comparisons_for_request_id(request.id)

            # prepare and return the list of comparisons
            comparisons = [self._generate_comparisons_(c, request) for c in comparisons]
            comparisons.sort(key=lambda x: x["result"], reverse=True)

        return comparisons

    def _generate_comparisons_(self, aux, request):
        """
        Generate comparisons
        :param aux:
        :param request:
        :return:
        """
        if aux.concat_a_request_id == request.id:
            new_dict = {
                "b_request_id": aux.concat_b_request_id,
                "concat_a_concat_id": aux.concat_a_concat_id,
                "concat_b_concat_id": aux.concat_b_concat_id,
                "tesla_id": self.data.get_request(aux.concat_b_request_id).user_id,
                "result": aux.concat_a_concat_b_result / 100.0,
                "type": aux.type.name
            }
        else:
            new_dict = {
                "b_request_id": aux.concat_b_request_id,
                "concat_a_concat_id": aux.concat_a_concat_id,
                "concat_b_concat_id": aux.concat_b_concat_id,
                "tesla_id": self.data.get_request(aux.concat_a_request_id).user_id,
                "result": aux.concat_b_concat_a_result / 100.0,
                "type": aux.type.name
            }
        return new_dict

    def get_audit_detail_data(self, original_request_id, b_request_id):
        """
        Get audit detail data
        :param original_request_id:
        :param comparison_id:
        :return:
        """
        src_text = None
        ref_text = None
        blocks = []

        # get the requests
        request = self.data.get_request_by_original_request_id(original_request_id)
        if request is not None:
            comparison = self.data.get_comparison_by_concat_b_request_id(b_request_id = b_request_id)
            if comparison is not None:
                concat_src = self.data.get_concat(comparison.concat_a_request_id,
                                                  comparison.concat_a_concat_id)
                concat_ref = self.data.get_concat(comparison.concat_b_request_id,
                                                  comparison.concat_b_concat_id)

                if comparison.concat_b_request_id == request.id:
                    concat_src, concat_ref = concat_ref, concat_src

                src_file_path = self.file_mngr.get_path_for_file(concat_src)

                # Obtain the path for the reference file
                ref_file_path = self.file_mngr.get_path_for_file(concat_ref)

                diff = self.comparator.get_diff(src_file_path, ref_file_path)

                diff = diff.decode('utf8').split("\n")[3:]

                indices = [i for i, x in enumerate(diff) if x == ""]

                for index in indices:

                    if index+2 < len(diff):
                        # get the head line that describes the equal lines from the first
                        # document and get the lines
                        src_lines = self.get_lines (diff[index+1])
                        # get the head line that describes the equal lines from the second
                        # document and get the lines
                        ref_lines = self.get_lines (diff[index+2])

                        if src_lines is not None and ref_lines is not None:
                            equal_block = {
                                'type': 'similarity',
                                'src_file_start_line': src_lines[0],
                                'src_file_end_line': src_lines[1],
                                'ref_file_start_line': ref_lines[0],
                                'ref_file_end_line': ref_lines[1]
                            }
                            blocks.append(equal_block)

                # do the same for statement if any. Set the type to 'statement'
                with codecs.open(src_file_path, mode='r') as file:
                    src_text = file.read()

                with codecs.open(ref_file_path, mode='r') as file:
                    ref_text = file.read()

                # self.data.close_session()

                return {"src_text": src_text, "ref_text": ref_text, "blocks": blocks }

        return None

    @staticmethod
    def get_lines(text):
        """
        Get lines
        :param text:
        :return:
        """
        try:
            # find the word 'line'
            index_of_lines_str = text.find('line ') + 5

            # extract only the part of the string that contains the line numbers
            text = text[index_of_lines_str:]

            text_splitted = text.split(' ')
            text = text_splitted[0]

            # parse the lines numbers, splitting by '-' and converting to numbers
            return list(map(int, text.split('-')))
        except IndexError:
            return None

    def get_diff(self, request_id1, file_id1, request_id2, file_id2):
        """
        Get the differences between two provided files
        :param request_id1:
        :param file_id1:
        :param request_id2:
        :param file_id2:
        :return:
        """

        src = TPTFile(request_id=request_id1, file_id=file_id1)
        ref = TPTFile(request_id=request_id2, file_id=file_id2)

        return self.processor.get_diff(src, ref)

    def add_request(self, request):
        """
        Add request
        :param request:
        :return:
        """
        # Launch the event for a new request
        self.events.onNewRequest.fire(request)

        # Store the request
        self.data.add_request(request)

        # Launch the event for a valid request
        self.events.onRequestValid.fire(request)

    def get_request_results(self, request_id):
        """
        Will return the results of a request or None if the request is not processed yet.
        """
        result = self.data.get_result(request_id)
        return result
