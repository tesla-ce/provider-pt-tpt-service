"""
Task compare module
"""
from tpt.commons import CmpResultStatusEnum, ReqStatusEnum


class Compare:
    """
    Task compare class
    """
    def __init__(self, data, comparator, log):
        self.data = data
        self.comparator = comparator
        self.log = log

    def __str__(self):
        return self.__class__.__name__

    def execute(self):
        """
        Compare request
        """
        comparison = self.data.get_next_pending_concat_comparison()
        result = False

        if comparison is not None:
            self.log.debug("COMPARING REQUEST {} VS {}".format(comparison.concat_a_request_id,
                                                               comparison.concat_b_request_id))

            result = self.comparator.process(comparison)
            if result is False:
                comparison.status = CmpResultStatusEnum.ERROR
                self.data.update_concat_cmp(comparison)

                req_a = self.data.get_request(comparison.concat_a_request_id)
                req_b = self.data.get_request(comparison.concat_b_request_id)

                if req_a.status == ReqStatusEnum.PROCESSING:
                    req_a.status = ReqStatusEnum.ERROR
                    self.data.update_request(req_a)

                if req_b.status == ReqStatusEnum.PROCESSING:
                    req_b.status = ReqStatusEnum.ERROR
                    self.data.update_request(req_b)

        return result
