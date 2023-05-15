"""
TPTComparator Module
"""
import os
import codecs
from tpt.commons import ReqStatusEnum, CmpTypeEnum, CmpResultStatusEnum, ReqCmpJobTypeEnum
from tpt.concatenator import TPTConcatenator
from tpt.statistics import TPTStatisticsHelper
from .sim_document_checker import SIMDocumentChecker


class TPTComparator:
    """
    TPTComparator class
    """
    def __init__(self, file_mngr, data, log, settings):

        self.file_mngr = file_mngr
        self.data = data
        self.log = log
        self.settings = settings

        self.concatenator = TPTConcatenator(self.file_mngr, self.data, self.log, self.settings)

        self.statistics = TPTStatisticsHelper(self.data, self.settings)

        self.checker = SIMDocumentChecker()

    def process_pending(self, comparison_type=ReqCmpJobTypeEnum.CONCATS):
        """
        Compare pending comparisons
        :param comparison_type:
        :return:
        """
        if comparison_type == ReqCmpJobTypeEnum.FILES:
            comparisons = self.data.get_pending_file_comparisons()

            for comparison in comparisons:
                self.process(comparison, comparison_type)
        else:
            comparisons = self.data.get_pending_concat_comparisons()
            for comparison in comparisons:
                self.process(comparison, comparison_type)

    def process(self, cmp, comparison_type=ReqCmpJobTypeEnum.CONCATS):
        """
        Process comparison
        :param cmp:
        :param comparison_type:
        :return:
        """
        cmp.status = CmpResultStatusEnum.PROCESSING

        if comparison_type == ReqCmpJobTypeEnum.FILES:
            src_req = self.data.get_request(cmp.file_a_request_id)
            ref_req = self.data.get_request(cmp.file_b_request_id)

            src = self.data.get_file(cmp.file_a_request_id, cmp.file_a_file_id)
            ref = self.data.get_file(cmp.file_b_request_id, cmp.file_b_file_id)
        else:
            src_req = self.data.get_request(cmp.concat_a_request_id)
            ref_req = self.data.get_request(cmp.concat_b_request_id)

            src = self.data.get_concat(cmp.concat_a_request_id, cmp.concat_a_concat_id)
            ref = self.data.get_concat(cmp.concat_b_request_id, cmp.concat_b_concat_id)

        # Obtain the path for the source file
        src_file_path = self.file_mngr.get_path_for_file(src)

        # Obtain the path for the reference file
        ref_file_path = self.file_mngr.get_path_for_file(ref)

        # Remove statement from files (if any)
        src_file_path = self.process_statement(src_file_path,
                                               self.file_mngr.get_path_for_activity(
                                                   src_req.activity) + '/statement.txt')
        ref_file_path = self.process_statement(ref_file_path,
                                               self.file_mngr.get_path_for_activity(
                                                   ref_req.activity) + '/statement.txt')

        # Compare the two files
        score_a_b, score_b_a = self.checker.compare(cmp.type.value, src_file_path, ref_file_path)

        # Store the result to the database
        self.data.update_score(src, ref, score_a_b, score_b_a, CmpResultStatusEnum.COMPLETED,
                               cmp.type.value)

        self.update_request_result(src_req, score_a_b, comparison_type)
        self.update_request_result(ref_req, score_b_a, comparison_type)

    def update_request_result(self, req, score, comparison_type):
        """
        Update request result
        :param req: Request
        :param score: Score
        :param comparison_type: Comparison type
        :return: None
        """
        if comparison_type == ReqCmpJobTypeEnum.FILES:

            update_score = self.data.check_update_files_result(req, score)

            if req.status == ReqStatusEnum.PROCESSED:
                if update_score:
                    self.data.set_request_pending_update(req, True)
            else:
                if self.data.not_completed_file_comparisons(req.id) == 0:
                    req.status = ReqStatusEnum.PROCESSED
                    self.data.set_request_pending_update(req, True)
        else:
            update_score = self.data.check_update_concats_result(req, score)
            if req.status == ReqStatusEnum.PROCESSED:
                if update_score:
                    self.data.set_request_pending_update(req, True)
            else:
                if self.data.not_completed_concat_comparisons(req.id) == 0:
                    req.status = ReqStatusEnum.PROCESSED
                    self.data.set_request_pending_update(req, True)

    def update_score(self, request, new_score, comparison_type):
        """
        Update score
        :param request: Request
        :param new_score: New score
        :param comparison_type: Comparison type
        :return: None
        """

        if comparison_type == ReqCmpJobTypeEnum.FILES:

            if new_score > request.files_result:
                request.files_result = new_score
                self.data.update_request(request)

        elif comparison_type == ReqCmpJobTypeEnum.CONCATS:
            if new_score > request.concats_result:
                request.concats_result = new_score
                self.data.update_request(request)

    def process_statement(self, file_path, statement_path):
        """
        Process statement
        :param file_path:
        :param statement_path:
        :return:
        """
        if os.path.isfile(statement_path): # The activity has statement
            # calc difference
            equal_lines = self.get_equal_content(file_path, statement_path)

            # new name for file without statement
            new_file_path = file_path + '.ws' # without_statement

            # substract statement
            string = codecs.open(file_path, 'r').read()

            for line in equal_lines:
                string = string.replace(line, '')

            with codecs.open(new_file_path, encoding='utf-8', mode="w") as file:
                file.write(string)

            file_path = new_file_path

        return file_path

    def get_diff(self, src, ref, comparison_type=CmpTypeEnum.TEXT):
        """
        Obtain the differences between two provided files
        :param src:
        :param ref:
        :param comparison_type:
        :return:
        """

        return self.checker.get_differences(comparison_type, src, ref)

    def get_equal_content(self, src, ref, comparison_type=CmpTypeEnum.TEXT):
        """
        Get equal content between two provided files
        :param src:
        :param ref:
        :param comparison_type:
        :return:
        """

        diff = self.get_diff(src, ref, comparison_type)

        lines = []

        new_line = []

        for line in diff.splitlines():

            if line.startswith('<'):
                new_line.append(line[1:])

            elif len(line) == 0:
                if len(new_line) > 0:
                    lines.append('\n'.join(new_line))
                    del new_line[:]

        return lines
