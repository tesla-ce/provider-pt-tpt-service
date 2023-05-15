"""
TPT Processor module
"""
import itertools
from tpt.commons import ReqStatusEnum, CmpTypeEnum
from tpt.concatenator import TPTConcatenator
from tpt.comparator import TPTComparator
from tpt.model import TPTConcatCmpResult
from tpt.statistics import TPTStatisticsHelper


class TPTProcessor:
    """
    TPT Processor class
    """
    def __init__(self, file_mngr, data, log, settings):
        self.file_mngr = file_mngr
        self.data = data
        self.log = log
        self.concatenator = TPTConcatenator(self.file_mngr, self.data, self.log, settings)
        self.statistics = TPTStatisticsHelper(self.data, settings)
        self.comparator = TPTComparator(self.file_mngr, self.data, self.log, settings)
        self.cmp_concats = []

    def process(self, request):
        """
        Process request
        :param request: Request
        :return: number of concats
        """
        count = self.calculate_comparisons(request)

        request.status = ReqStatusEnum.PROCESSING
        if count == 0:
            request.status = ReqStatusEnum.PROCESSED

        self.data.update_request(request)
        return count

    def calculate_comparisons(self, request):
        """
        Calculate comparisons
        :param request: Request
        :return: number of concats
        """
        related_reqs = self.data.get_related_requests(request)
        aux = [self.get_cmp_concats(request, x) for x in related_reqs]
        cmp_concats = list(itertools.chain(*aux))
        self.data.add_cmp_concats(cmp_concats)
        len_concats = len(cmp_concats)

        return len_concats

    def get_cmp_concats(self, src, ref):
        """
        Get comparison concats
        :param src: source
        :param ref: reference
        :return: array of concats
        """
        if src.id > ref.id:
            src, ref = ref, src

        self.cmp_concats = []

        activity_cmp_type = src.activity.activity_type

        if activity_cmp_type == CmpTypeEnum.AUTO:
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.TEXT)
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.C)
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.CPP)
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.JAVA)
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.M2)
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.ASSEMBLER)
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.MIRANDA)
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.LISP)

        elif activity_cmp_type == CmpTypeEnum.TEXT_ONLY:
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=CmpTypeEnum.TEXT_ONLY)
        else:
            self.calculate_cmp_concats(src=src, ref=ref, cmp_type=activity_cmp_type)

        return self.cmp_concats

    def calculate_cmp_concats(self, src, ref, cmp_type):
        """
        Calculate cmp concats by type
        :param src: source
        :param ref: reference
        :param cmp_type: comparison type
        :return: None
        """
        concat1 = self.get_request_concat_by_type(src, cmp_type)
        concat2 = self.get_request_concat_by_type(ref, cmp_type)

        if concat1 is not None and concat1.size > 0 and concat2 is not None and concat2.size > 0:
            self.cmp_concats.append(TPTConcatCmpResult(concat_a_concat_id=concat1.concat_id,
                                                       concat_a_request_id=concat1.request_id,
                                                       concat_b_concat_id=concat2.concat_id,
                                                       concat_b_request_id=concat2.request_id,
                                                       concat_a_concat_b_result=0,
                                                       concat_b_concat_a_result=0,
                                                       type=cmp_type))

    def get_request_concat_by_type(self, request, concat_type):
        """
        Get concats by type
        :param request: request
        :param concat_type: concat type
        :return:
        """
        concats = list(filter(lambda x: x.type == concat_type, request.concats))
        concat = concats[0] if len(concats) > 0 else None

        if len(concats) == 0:
            concat = self.concatenator.create_concatenated_file(request, concat_type)

        return concat
