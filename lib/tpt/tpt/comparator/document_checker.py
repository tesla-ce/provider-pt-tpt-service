"""
DocumentChecker module
"""
from abc import abstractmethod


class DocumentChecker:
    """
    DocumentChecker class
    """
    @abstractmethod
    def compare(self, comparison_type, file_src, file_ref):
        """
        Compare between source and reference file
        :param comparison_type:
        :param file_src:
        :param file_ref:
        :return:
        """

    @abstractmethod
    def get_differences(self, comparison_type, file_src, file_ref):
        """
        Get differences between source and reference file
        :param comparison_type:
        :param file_src:
        :param file_ref:
        :return:
        """
