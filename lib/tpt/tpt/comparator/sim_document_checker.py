"""
SIMDocumentChecker module
"""
from .sim import SIM
from .document_checker import DocumentChecker


class SIMDocumentChecker(DocumentChecker):
    """
    SIMDocumentChecker class
    """
    def __init__(self, thr=None, page_width=80, min_run_size=24):
        self.engine = SIM()
        self.thr = thr
        self.page_width = page_width
        self.min_run_size = min_run_size
        super(DocumentChecker, self)

    def compare(self, comparison_type, file_src, file_ref):
        """
        Compare between source and reference file
        :param comparison_type:
        :param file_src:
        :param file_ref:
        :return:
        """
        return self.engine.cmp_files(comparison_type, file_src, file_ref)

    def get_differences(self, comparison_type, file_src, file_ref):
        """
        Get differences between source and reference file
        :param comparison_type:
        :param file_src:
        :param file_ref:
        :return:
        """
        return self.engine.get_diff(comparison_type.value, file_src, file_ref)
