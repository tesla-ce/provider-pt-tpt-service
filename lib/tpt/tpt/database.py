"""
DBAccess module
"""
import ast
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, ResourceClosedError, ProgrammingError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import SQLAlchemyError
import tpt.model as model
from tpt.commons import ReqStatusEnum, ActContextEnum, CmpResultStatusEnum, TPTException
from tpt.model import TPTFile, TPTConcat
from tpt.model.util import DB_SCHEMA


class DBAccess:
    """
    DBAccess class
    """
    def __init__(self, engine, log, create_db=False):
        # engine.dispose()

        self.engine = engine

        # create Session()
        aux_session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.conn = self.engine.connect()
        self.session = aux_session(bind=self.conn)
        self.log = log

        if create_db is True:
            # if not exist create schema
            try:
                if not engine.dialect.has_schema(engine, DB_SCHEMA):
                    engine.execute(CreateSchema(DB_SCHEMA))
            except AttributeError as err:
                self.log.warning("Schema can not be created: {}".format(err))

            model.BASE.metadata.create_all(self.engine)

    def close_session(self):
        """
        Close session
        :return:
        """

        try:
            self.session.close()
        except Exception as err:
            self.log.exception(err)

        try:
            self.conn.invalidate()
            self.conn.close()
        except Exception as err:
            self.log.exception(err)

    def add_or_update_request(self, request):
        """
        Add or update request
        :param request:
        :return:
        """
        try:
            if request.id is None:
                self.session.add(request)
            else:
                self.session.merge(request)
            self.session.commit()
            self.session.flush()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

        return request

    def add_statistic(self, statistic):
        """
        Add statistic
        :param statistic:
        :return:
        """
        try:
            self.session.add(statistic)
            self.session.commit()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def add_file(self, file):
        """
        Add file
        :param file:
        :return:
        """
        try:
            self.session.add(file)
            self.session.commit()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def add_concat(self, concat):
        """
        Add concat
        :param concat:
        :return:
        """
        try:
            self.session.add(concat)
            self.session.commit()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_prepared_request(self):
        """
        Get prepared request
        :return:
        """
        request = None
        # lock all pending requests
        requests = self.session.query(model.TPTRequest).with_for_update().filter(
            model.TPTRequest.status == ReqStatusEnum.PREPARED).order_by("status", "created_at").\
            all()

        count = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.status == ReqStatusEnum.PROCESSING).count()

        if len(requests) > 0 and count == 0:
            # there are no other thread processing any request.
            request = requests[0]
            request.status = ReqStatusEnum.PROCESSING

        self.session.commit()
        return request

    def get_not_completed_requests_count(self):
        """
        Get not completed request count
        :return:
        """
        # lock all pending requests
        count = self.session.query(model.TPTRequest).filter(
            or_(model.TPTRequest.status == ReqStatusEnum.PROCESSED,
                model.TPTRequest.status == ReqStatusEnum.ERROR)).count()

        return count

    def get_request(self, request_id):
        """
        Get request
        :param request_id:
        :return:
        """
        return self.session.query(model.TPTRequest).get(request_id)

    def get_pending_extract_requests(self):
        """
        Get pending extract request in extract requests
        :return:
        """
        return self.session.query(model.TPTRequest).filter(
            model.TPTRequest.status == ReqStatusEnum.PENDING_EXTRACT).all()

    def get_file(self, request_id, file_id):
        """
        Get file
        :param request_id:
        :param file_id:
        :return:
        """
        return self.session.query(model.TPTFile).filter(TPTFile.request_id == request_id,
                                                        TPTFile.file_id == file_id).first()

    def get_concat(self, request_id, concat_id):
        """
        Get concat
        :param request_id:
        :param concat_id:
        :return:
        """
        return self.session.query(model.TPTConcat).filter(TPTConcat.request_id == request_id,
                                                          TPTConcat.concat_id == concat_id).first()

    def get_activity(self, activity_id):
        """
        Get activity
        :param activity_id:
        :return:
        """
        activity_id = str(activity_id)
        activity = self.session.query(model.TPTActivity).get(activity_id)
        self.session.commit()
        self.session.flush()
        return activity

    def add_or_update_activity(self, activity):
        """
        Add or update activity
        :param activity:
        :return:
        """

        act = activity

        try:
            self.session.merge(activity)
            self.session.commit()
            self.session.flush()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

        return act

    def get_file_score(self, file_a, file_b):
        """
        Get file score
        :param file_a:
        :param file_b:
        :return:
        """
        inverse_order = file_a.request_id > file_b.request_id

        file_a_file_id = file_b.file_id if inverse_order else file_a.file_id
        file_a_request_id = file_b.request_id if inverse_order else file_a.request_id
        file_b_file_id = file_a.file_id if inverse_order else file_b.file_id
        file_b_request_id = file_a.request_id if inverse_order else file_b.request_id

        try:
            result = self.session.query(model.TPTFileCmpResult).filter(
                model.TPTFileCmpResult.file_a_file_id == file_a_file_id,
                model.TPTFileCmpResult.file_a_request_id == file_a_request_id,
                model.TPTFileCmpResult.file_b_file_id == file_b_file_id,
                model.TPTFileCmpResult.file_b_request_id == file_b_request_id).first()

            self.session.commit()

            return result.file_b_file_a_result if inverse_order else result.file_a_file_b_result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_pending_file_comparisons(self):
        """
        Get pending file comparisons
        :return:
        """
        try:
            result = self.session.query(model.TPTFileCmpResult).filter(
                model.TPTFileCmpResult.status == CmpResultStatusEnum.PENDING).all()

            self.session.commit()
            return result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_next_pending_concat_comparison(self):
        """
        Get next pending concat comparison
        :return:
        """
        try:
            result = self.session.query(model.TPTConcatCmpResult).with_for_update().\
                filter(model.TPTConcatCmpResult.status == CmpResultStatusEnum.PENDING).first()

            if result is not None:
                result.status = CmpResultStatusEnum.PROCESSING

            self.session.commit()
            return result
        except ResourceClosedError as err:
            return None
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_pending_concat_comparisons(self):
        """
        Get pending concat comparisons
        :return:
        """
        try:
            result = self.session.query(model.TPTConcatCmpResult).filter(
                model.TPTConcatCmpResult.status == CmpResultStatusEnum.PENDING).all()

            return result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_concat_score_deprecated(self, concat_a, concat_b):
        """
        Get concat score deprecated
        :param concat_a:
        :param concat_b:
        :return:
        """
        inverse_order = concat_a.request_id > concat_b.request_id

        concat_a_concat_id = concat_b.concat_id if inverse_order else concat_a.concat_id
        concat_a_request_id = concat_b.request_id if inverse_order else concat_a.request_id
        concat_b_concat_id = concat_a.concat_id if inverse_order else concat_b.concat_id
        concat_b_request_id = concat_a.request_id if inverse_order else concat_b.request_id

        try:
            result = self.session.query(model.TPTConcatCmpResult).filter(
                model.TPTConcatCmpResult.concat_a_concat_id == concat_a_concat_id,
                model.TPTConcatCmpResult.concat_a_request_id == concat_a_request_id,
                model.TPTConcatCmpResult.concat_b_concat_id == concat_b_concat_id,
                model.TPTConcatCmpResult.concat_b_request_id == concat_b_request_id).first()

            self.session.commit()

            return result.concat_b_concat_a_result if inverse_order else \
                result.concat_a_concat_b_result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def add_score(self, item_a, item_b, score_a_b, score_b_a, cmptype):
        """
        Add score
        :param item_a:
        :param item_b:
        :param score_a_b:
        :param score_b_a:
        :param cmptype:
        :return:
        """

        if isinstance(item_a, TPTFile) and isinstance(item_b, TPTFile):
            self.add_file_score(item_a, item_b, score_a_b, score_b_a, cmptype)

        elif isinstance(item_a, TPTConcat) and isinstance(item_b, TPTConcat):
            self.add_concat_score(item_a, item_b, score_a_b, score_b_a, cmptype)

    def update_score(self, item_a, item_b, score_a_b, score_b_a, status, cmptype):
        """
        Update score
        :param item_a:
        :param item_b:
        :param score_a_b:
        :param score_b_a:
        :param status:
        :param cmptype:
        :return:
        """
        if isinstance(item_a, TPTFile) and isinstance(item_b, TPTFile):
            self.update_file_score(item_a, item_b, score_a_b, score_b_a, status)

        elif isinstance(item_a, TPTConcat) and isinstance(item_b, TPTConcat):
            self.update_concat_score(item_a, item_b, score_a_b, score_b_a, status, cmptype)

    def add_file_score(self, file_a, file_b, score_a_b, score_b_a, score_type):
        """
        Add file score
        :param file_a:
        :param file_b:
        :param score_a_b:
        :param score_b_a:
        :param score_type:
        :return:
        """
        try:
            inverse_order = file_a.request_id > file_b.request_id

            if inverse_order:
                cmp_result = model.TPTFileCmpResult(file_a_file_id=file_b.file_id,
                                                    file_a_request_id=file_b.request_id,
                                                    file_b_file_id=file_a.file_id,
                                                    file_b_request_id=file_a.request_id,
                                                    file_a_file_b_result=score_b_a,
                                                    file_b_file_a_result=score_a_b,
                                                    type=score_type)
                self.session.add(cmp_result)
            else:
                cmp_result = model.TPTFileCmpResult(file_a_file_id=file_a.file_id,
                                                    file_a_request_id=file_a.request_id,
                                                    file_b_file_id=file_b.file_id,
                                                    file_b_request_id=file_b.request_id,
                                                    file_a_file_b_result=score_a_b,
                                                    file_b_file_a_result=score_b_a,
                                                    type=score_type)

                self.session.add(cmp_result)

            self.session.commit()

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def add_concat_score(self, concat_a, concat_b, score_a_b, score_b_a, score_type):
        """
        Add concat score
        :param concat_a:
        :param concat_b:
        :param score_a_b:
        :param score_b_a:
        :param score_type:
        :return:
        """
        try:

            inverse_order = concat_a.request_id > concat_b.request_id

            if inverse_order:
                cmp_result = model.TPTConcatCmpResult(concat_a_concat_id=concat_b.concat_id,
                                                      concat_a_request_id=concat_b.request_id,
                                                      concat_b_concat_id=concat_a.concat_id,
                                                      concat_b_request_id=concat_a.request_id,
                                                      concat_a_concat_b_result=score_b_a,
                                                      concat_b_concat_a_result=score_a_b,
                                                      type=score_type)

                self.session.add(cmp_result)

            else:

                cmp_result = model.TPTConcatCmpResult(concat_a_concat_id=concat_a.concat_id,
                                                      concat_a_request_id=concat_a.request_id,
                                                      concat_b_concat_id=concat_b.concat_id,
                                                      concat_b_request_id=concat_b.request_id,
                                                      concat_a_concat_b_result=score_a_b,
                                                      concat_b_concat_a_result=score_b_a,
                                                      type=score_type)

                self.session.add(cmp_result)

            self.session.commit()

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def add_concat_cmps(self, concat_cmps):
        """
        Add concat comparisons
        :param concat_cmps:
        :return:
        """
        try:
            for cmp in concat_cmps:
                self.session.add(cmp)

            self.session.commit()

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def update_file_score(self, file_a, file_b, score_a_b, score_b_a, status):
        """
        Update file score
        :param file_a:
        :param file_b:
        :param score_a_b:
        :param score_b_a:
        :param status:
        :return:
        """
        try:

            inverse_order = file_a.request_id > file_b.request_id

            if inverse_order:

                cmp_result = self.session.query(model.TPTFileCmpResult).filter(
                    model.TPTFileCmpResult.file_a_file_id == file_b.file_id,
                    model.TPTFileCmpResult.file_a_request_id == file_b.request_id,
                    model.TPTFileCmpResult.file_b_file_id == file_a.file_id,
                    model.TPTFileCmpResult.file_b_request_id == file_a.request_id).first()

                if cmp_result is None:
                    cmp_result = model.TPTFileCmpResult(file_a_file_id=file_b.file_id,
                                                        file_a_request_id=file_b.request_id,
                                                        file_b_file_id=file_a.file_id,
                                                        file_b_request_id=file_a.request_id,
                                                        file_a_file_b_result=score_b_a,
                                                        file_b_file_a_result=score_a_b,
                                                        status=status)

                    self.session.add(cmp_result)

                else:
                    cmp_result.file_a_file_b_result = score_b_a
                    cmp_result.file_b_file_a_result = score_a_b
                    cmp_result.status = status

            else:
                cmp_result = self.session.query(model.TPTFileCmpResult).filter(
                    model.TPTFileCmpResult.file_a_file_id == file_a.file_id,
                    model.TPTFileCmpResult.file_a_request_id == file_a.request_id,
                    model.TPTFileCmpResult.file_b_file_id == file_b.file_id,
                    model.TPTFileCmpResult.file_b_request_id == file_b.request_id).first()

                if cmp_result is None:
                    cmp_result = model.TPTFileCmpResult(file_a_file_id=file_a.file_id,
                                                        file_a_request_id=file_a.request_id,
                                                        file_b_file_id=file_b.file_id,
                                                        file_b_request_id=file_b.request_id,
                                                        file_a_file_b_result=score_a_b,
                                                        file_b_file_a_result=score_b_a,
                                                        status=status)

                    self.session.add(cmp_result)

                else:

                    cmp_result.file_a_file_b_result = score_a_b
                    cmp_result.file_b_file_a_result = score_b_a
                    cmp_result.status = status

            self.session.commit()

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def add_cmp_concats(self, cmp_concats):
        """
        Add comparison concats
        :param cmp_concats:
        :return:
        """
        try:
            self.session.bulk_save_objects(cmp_concats)
            self.session.commit()

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def update_concat_score(self, concat_a, concat_b, score_a_b, score_b_a, status, concat_type):
        """
        Update concat score
        :param concat_a:
        :param concat_b:
        :param score_a_b:
        :param score_b_a:
        :param status:
        :param concat_type:
        :return:
        """
        try:

            inverse_order = concat_a.request_id > concat_b.request_id

            if inverse_order:
                cmp_result = self.session.query(model.TPTConcatCmpResult).filter(
                    model.TPTConcatCmpResult.concat_a_concat_id == concat_b.concat_id,
                    model.TPTConcatCmpResult.concat_a_request_id == concat_b.request_id,
                    model.TPTConcatCmpResult.concat_b_concat_id == concat_a.concat_id,
                    model.TPTConcatCmpResult.concat_b_request_id == concat_a.request_id).first()

                if cmp_result is None:

                    cmp_result = model.TPTConcatCmpResult(concat_a_concat_id=concat_b.concat_id,
                                                          concat_a_request_id=concat_b.request_id,
                                                          concat_b_concat_id=concat_a.concat_id,
                                                          concat_b_request_id=concat_a.request_id,
                                                          concat_a_concat_b_result=score_b_a,
                                                          concat_b_concat_a_result=score_a_b,
                                                          status=status,
                                                          type=concat_type)

                    self.session.add(cmp_result)

                else:

                    cmp_result.concat_a_concat_b_result = score_b_a
                    cmp_result.concat_b_concat_a_result = score_a_b
                    cmp_result.status = status

            else:

                cmp_result = self.session.query(model.TPTConcatCmpResult).filter(
                    model.TPTConcatCmpResult.concat_a_concat_id == concat_a.concat_id,
                    model.TPTConcatCmpResult.concat_a_request_id == concat_a.request_id,
                    model.TPTConcatCmpResult.concat_b_concat_id == concat_b.concat_id,
                    model.TPTConcatCmpResult.concat_b_request_id == concat_b.request_id).first()

                if cmp_result is None:

                    cmp_result = model.TPTConcatCmpResult(concat_a_concat_id=concat_a.concat_id,
                                                          concat_a_request_id=concat_a.request_id,
                                                          concat_b_concat_id=concat_b.concat_id,
                                                          concat_b_request_id=concat_b.request_id,
                                                          concat_a_concat_b_result=score_a_b,
                                                          concat_b_concat_a_result=score_b_a,
                                                          status=status, type=concat_type)

                    self.session.add(cmp_result)

                else:

                    cmp_result.concat_a_concat_b_result = score_a_b
                    cmp_result.concat_b_concat_a_result = score_b_a
                    cmp_result.status = status

            self.session.commit()

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def update_status(self, request, new_status):
        """
        Update status
        :param request:
        :param new_status:
        :return:
        """
        try:
            self.session.merge(request)
            request.status = new_status
            self.session.commit()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def update_concat_cmp(self, concat_cmp):
        """
        Update concat comparison
        :param concat_cmp:
        :return:
        """

        try:
            self.session.merge(concat_cmp)
            self.session.commit()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def update_request(self, request):
        """
        Update request
        :param request:
        :return:
        """
        try:
            self.session.merge(request)
            self.session.commit()
        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_request_files(self, request):
        """
        Get request files
        :param request:
        :return:
        """
        files = []
        req = self.session.query(model.TPTRequest).get(request.id)
        if req is not None:
            files = req.files
        return files

    def get_request_concats(self, request):
        """
        Get request concats
        :param request:
        :return:
        """
        concats = []
        req = self.session.query(model.TPTRequest).get(request.id)
        if req is not None:
            concats = req.concats
        return concats

    def calc_and_update_files_score_deprecated(self, request, update_time=False):
        """
        Calc and update files score deprecated
        :param request:
        :param update_time:
        :return:
        """
        try:

            # Force to reload the dependencies
            req = self.session.query(model.TPTRequest).get(request.id)

            # The global score / % of plagiarism is calculed as the maximum % of each file in
            # the request, which in turn is calculated as the maximum value of each comparison
            # of that file with other requests.

            # Get the maximum value for each file
            res = []
            elapsed_time = 0
            comparisons = 0

            for file in req.files:
                max_score = 0

                # Find TPTCmpResult rows where the file acts as file_a, and consider
                # file_a_file_b_result as score
                f_results = self.session.query(model.TPTFileCmpResult).filter(
                    model.TPTFileCmpResult.file_a_file_id == file.file_id,
                    model.TPTFileCmpResult.file_a_request_id == file.request_id)

                comparisons = comparisons + len(f_results.all())

                for s_res in f_results:
                    if s_res.file_a_file_b_result > max_score:
                        max_score = s_res.file_a_file_b_result

                    elapsed_time += (s_res.elapsed_time if s_res.elapsed_time is not None else 0)


                # Find TPTCmpResult rows where the file acts as file_b, and consider
                # file_b_file_a_result as score
                f_results = self.session.query(model.TPTFileCmpResult).filter(
                    model.TPTFileCmpResult.file_b_file_id == file.file_id,
                    model.TPTFileCmpResult.file_b_request_id == file.request_id)

                comparisons = comparisons + len(f_results.all())

                for s_res in f_results:
                    if s_res.file_b_file_a_result > max_score:
                        max_score = s_res.file_b_file_a_result

                    elapsed_time += (s_res.elapsed_time if s_res.elapsed_time is not None else 0)

                res.append(max_score)

            # Get the maximum value as final result
            request.files_result = max(res) if len(res) > 0 else 0

            if update_time:
                request.files_elapsed_time = elapsed_time

            request.files_comparisons = comparisons

            self.session.commit()

            return request.files_result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def calc_and_update_concats_score_deprecated(self, request, update_time=False):
        """
        Calc and update concats score deprecated
        :param request:
        :param update_time:
        :return:
        """
        try:

            # Force to reload the dependencies
            req = self.session.query(model.TPTRequest).get(request.id)

            # The global score / % of plagiarism is calculed as the maximum % of each concat in
            # the request, which in turn is calculated as the maximum value of each comparison
            # of that concat with other requests.

            # Get the maximum value for each concat
            res = []
            elapsed_time = 0
            comparisons = 0

            for file in req.concats:
                max_score = 0

                # Find TPTCmpResult rows where the concat acts as concat_a, and consider
                # concat_a_concat_b_result as score
                f_results = self.session.query(model.TPTConcatCmpResult).filter(
                    model.TPTConcatCmpResult.concat_a_concat_id == file.concat_id,
                    model.TPTConcatCmpResult.concat_a_request_id == file.request_id)

                comparisons = comparisons + len(f_results.all())

                for s_res in f_results:
                    if s_res.concat_a_concat_b_result > max_score:
                        max_score = s_res.concat_a_concat_b_result

                    elapsed_time += (s_res.elapsed_time if s_res.elapsed_time is not None else 0)

                # Find TPTCmpResult rows where the concat acts as concat_b, and consider
                # concat_b_concat_a_result as score
                f_results = self.session.query(model.TPTConcatCmpResult).filter(
                    model.TPTConcatCmpResult.concat_b_concat_id == file.concat_id,
                    model.TPTConcatCmpResult.concat_b_request_id == file.request_id)

                comparisons = comparisons + len(f_results.all())

                for s_res in f_results:
                    if s_res.concat_b_concat_a_result > max_score:
                        max_score = s_res.concat_b_concat_a_result

                    elapsed_time += (s_res.elapsed_time if s_res.elapsed_time is not None else 0)

                res.append(max_score)

            # Get the maximum value as final result
            request.concats_result = max(res) if len(res) > 0 else 0

            if update_time:
                request.concats_elapsed_time = elapsed_time

            request.concats_comparisons = comparisons

            self.session.commit()

            return request.concats_result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def recalc_request_score(self, request_id):
        """
        Recalc request score
        :param request_id:
        :return:
        """
        try:

            score1 = self.session.query(func.max(
                model.TPTConcatCmpResult.concat_a_concat_b_result).filter(
                model.TPTConcatCmpResult.concat_a_request_id == request_id))

            score2 = self.session.query(func.max(
                model.TPTConcatCmpResult.concat_a_concat_b_result).filter(
                model.TPTConcatCmpResult.concat_b_request_id == request_id))

            return max(score1, score2)

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_related_requests(self, request):
        """
        Get related requests
        :param request:
        :return:
        """
        reqs = None

        if request.activity.context == ActContextEnum.ACTIVITY:
            reqs = self.session.query(model.TPTRequest).filter(
                model.TPTRequest.id != request.id,
                model.TPTRequest.activity_id == request.activity_id,
                or_(model.TPTRequest.status == ReqStatusEnum.PROCESSING,
                    model.TPTRequest.status == ReqStatusEnum.PROCESSED)).all()

        elif request.activity.context == ActContextEnum.COURSE:
            # Get all the activities from the course
            act_ids = self.session.query(model.TPTActivity.activity_id).filter(
                model.TPTActivity.course_id == request.activity.course_id).all()

            if act_ids:
                reqs = self.session.query(model.TPTRequest).filter(
                    model.TPTRequest.id != request.id,
                    model.TPTRequest.activity_id.in_([e[0] for e in act_ids]),
                    or_(model.TPTRequest.status == ReqStatusEnum.PROCESSING,
                        model.TPTRequest.status == ReqStatusEnum.PROCESSED)).all()

        elif request.activity.context == ActContextEnum.ACTIVITY_LIST:
            # Use the provided list of activities
            config = ast.literal_eval(request.activity.config)
            activity_list = config['context']['activity_list']
            reqs = self.session.query(model.TPTRequest).filter(
                model.TPTRequest.id != request.id,
                model.TPTRequest.activity_id.in_(activity_list),
                or_(model.TPTRequest.status == ReqStatusEnum.PROCESSING,
                    model.TPTRequest.status == ReqStatusEnum.PROCESSED)).all()

        elif request.activity.context == ActContextEnum.ALL:
            # Compare with any other request
            reqs = self.session.query(model.TPTRequest).filter(
                model.TPTRequest.id != request.id,
                or_(model.TPTRequest.status == ReqStatusEnum.PROCESSING,
                    model.TPTRequest.status == ReqStatusEnum.PROCESSED)).all()

        # remove requests with the same activity_id and student_id
        return filter(lambda x: x.activity_id != request.activity_id or
                                x.user_id != request.user_id, reqs)

    def not_completed_file_comparisons(self, request_id):
        """
        Not completed file comparisons
        :param request_id:
        :return:
        """
        try:
            result = self.session.query(model.TPTFileCmpResult).filter(
                model.TPTFileCmpResult.status != CmpResultStatusEnum.COMPLETED,
                model.TPTFileCmpResult.status != CmpResultStatusEnum.ERROR,
                or_(model.TPTFileCmpResult.file_a_request_id == request_id,
                    model.TPTFileCmpResult.file_b_request_id == request_id)).count()

            self.session.commit()

            return result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def not_completed_concat_comparisons(self, request_id):
        """
        Not completed concat comparisons
        :param request_id:
        :return:
        """
        try:
            result = self.session.query(model.TPTConcatCmpResult).filter(
                model.TPTConcatCmpResult.status != CmpResultStatusEnum.COMPLETED,
                model.TPTConcatCmpResult.status != CmpResultStatusEnum.ERROR,
                or_(model.TPTConcatCmpResult.concat_a_request_id == request_id,
                    model.TPTConcatCmpResult.concat_b_request_id == request_id)).count()

            self.session.commit()

            return result

        except SQLAlchemyError as err:
            self.log.exception(err)
            self.session.rollback()
            raise TPTException(err) from err

    def get_next_pending_update_request(self):
        """
        Get next pending update request
        :return:
        """
        session = self.session
        req = session.query(model.TPTRequest).filter(
            model.TPTRequest.pending_update == True,
            model.TPTRequest.status != ReqStatusEnum.UPDATING).order_by("created_at").first()

        if req is not None:
            req_result = req.concats_result
            req_id = req.id

            parent_request_id = req.original_request_id.split('__')[0]

            req = session.query(model.TPTRequest).with_for_update().filter(
                model.TPTRequest.pending_update == True,
                model.TPTRequest.status != ReqStatusEnum.UPDATING,
                model.TPTRequest.original_request_id.like(parent_request_id+"%")
            ).order_by(model.TPTRequest.concats_result.desc()).first()

            if req and (req_result >= req.concats_result or req_id == req.id):
                req.status = ReqStatusEnum.UPDATING
                req.pending_update = False

        session.commit()

        return req

    def get_pending_update_requests(self):
        """
        Get pending update requests
        :return:
        """
        req = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.pending_update is True).order_by("created_at").all()

        return req

    def check_update_files_result(self, req, score):
        """
        Check update files result
        :param req:
        :param score:
        :return:
        """
        update_score = False

        req = self.session.query(model.TPTRequest).with_for_update().filter(
            model.TPTRequest.id == req.id).first()

        if req is not None:
            update_score = score > req.files_result
            if update_score:
                req.files_result = score

        self.session.commit()

        return update_score

    def check_update_concats_result(self, req, score):
        """
        Check update concats result
        :param req:
        :param score:
        :return:
        """
        update_score = False

        req = self.session.query(model.TPTRequest).with_for_update().filter(
            model.TPTRequest.id == req.id).first()

        if req is not None:
            update_score = score > req.concats_result
            if update_score:
                req.concats_result = score

        self.session.commit()

        return update_score

    def get_comparison_by_id(self, cmp_id):
        """
        Get comparison by id
        :param cmp_id:
        :return:
        """
        return self.session.query(model.TPTConcatCmpResult).filter(
            model.TPTConcatCmpResult.id == cmp_id).first()

    def get_comparison_by_concat_b_concat_id(self, concat_b_concat_id):
        """
        Get comparison by id
        :param cmp_id:
        :return:
        """
        return self.session.query(model.TPTConcatCmpResult).filter(
            model.TPTConcatCmpResult.concat_b_concat_id == concat_b_concat_id).first()

    def get_comparison_by_concat_b_request_id(self, b_request_id):
        """
        Get comparison by id
        :param cmp_id:
        :return:
        """
        return self.session.query(model.TPTConcatCmpResult).filter(
            model.TPTConcatCmpResult.concat_b_request_id == b_request_id).first()

    def get_comparisons_for_request_id(self, request_id):
        """
        Get comparisons for request id
        :param request_id:
        :return:
        """
        return self.session.query(model.TPTConcatCmpResult).filter(
            model.TPTConcatCmpResult.status == CmpResultStatusEnum.COMPLETED,
            or_(model.TPTConcatCmpResult.concat_a_request_id == request_id,
                model.TPTConcatCmpResult.concat_b_request_id == request_id)).all()

    def get_request_by_original_request_id(self, original_request_id):
        """
        Get request by original request id
        :param original_request_id:
        :return:
        """
        return self.session.query(model.TPTRequest).filter(
            model.TPTRequest.original_request_id == original_request_id).first()

    def set_request_pending_update(self, req, pending):
        """
        Set request pending update
        :param req:
        :param pending:
        :return:
        """
        req = self.session.query(model.TPTRequest).with_for_update().filter(
            model.TPTRequest.id == req.id).first()

        if req is not None:
            req.pending_update = pending

        self.session.commit()

    def get_activities_with_requests_from_user_id(self, user_id):
        """
        Get activities with requests from user id
        :param user_id:
        :return:
        """
        activities = self.session.query(model.TPTRequest.activity_id).filter(
            model.TPTRequest.user_id == user_id).distinct(model.TPTRequest.activity_id).all()

        self.session.commit()

        return map(lambda x: x[0], activities)

    def delete_by_user_id(self, user_id):
        """
        Delete by user id
        :param user_id:
        :return:
        """
        # get requests
        requests = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.user_id == user_id).all()

        self.session.commit()
        requests_affected = self.delete_requests(requests, delete_requests=True)

        return requests_affected

    def delete_by_activity_id(self, activity_id, delete_requests=False):
        """
        Delete by activity id
        :param activity_id:
        :param delete_requests:
        :return:
        """
        # get requests
        requests = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.activity_id == activity_id).all()
        self.session.commit()

        requests_affected = self.delete_requests(requests, delete_requests=delete_requests)

        return requests_affected

    def delete_activity(self, activity_id):
        """

        :param activity_id:
        :return:
        """
        activity_id = str(activity_id)
        self.session.query(model.TPTActivity).filter(model.TPTActivity.activity_id == activity_id)\
            .delete()
        self.session.commit()

    def delete_requests(self, requests, delete_requests):
        """
        Delete requests
        :param requests:
        :param delete_requests:
        :return:
        """
        requests_affected = []

        for request in requests:
            # calculate requests affected
            reqs = self.session.query(model.TPTConcatCmpResult.concat_b_request_id).filter(
                model.TPTConcatCmpResult.concat_a_request_id == request.id).all()

            requests_affected.extend(aux for aux in reqs if aux not in requests_affected)

            reqs = self.session.query(model.TPTConcatCmpResult.concat_a_request_id).filter(
                model.TPTConcatCmpResult.concat_b_request_id == request.id).all()

            requests_affected.extend(aux for aux in reqs if aux not in requests_affected)

            reqs = self.session.query(model.TPTFileCmpResult.file_b_request_id).filter(
                model.TPTFileCmpResult.file_a_request_id == request.id).all()

            requests_affected.extend(aux for aux in reqs if aux not in requests_affected)

            reqs = self.session.query(model.TPTFileCmpResult.file_a_request_id).filter(
                model.TPTFileCmpResult.file_b_request_id == request.id).all()

            requests_affected.extend(aux for aux in reqs if aux not in requests_affected)

            # delete comparisons
            if delete_requests is True:
                self.session.query(model.TPTConcatCmpResult).filter(
                    or_(model.TPTConcatCmpResult.concat_a_request_id == request.id,
                        model.TPTConcatCmpResult.concat_b_request_id == request.id)).delete()

                self.session.query(model.TPTFileCmpResult).filter(
                    or_(model.TPTFileCmpResult.file_a_request_id == request.id,
                        model.TPTFileCmpResult.file_b_request_id == request.id)).delete()

                # delete files / concats
                self.session.query(model.TPTConcat).filter(
                    model.TPTConcat.request_id == request.id).delete()

                self.session.query(model.TPTFile).filter(
                    model.TPTFile.request_id == request.id).delete()

                # delete request
                self.session.delete(request)

        self.session.commit()

        return requests_affected

    def get_health_data(self):
        """
        Get health data
        :return:
        """
        req_pending_update = self.session.query(model.TPTRequest).filter\
            (model.TPTRequest.pending_update is True).count()

        # lock all pending requests
        req_pending_analyze = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.status == ReqStatusEnum.PENDING).count()

        req_analyzed = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.status == ReqStatusEnum.PROCESSED).count()

        req_processing = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.status == ReqStatusEnum.PROCESSING).count()

        req_prepared = self.session.query(model.TPTRequest).filter(
            model.TPTRequest.status == ReqStatusEnum.PREPARED).count()

        return {"requests": {"pending_update": req_pending_update,
                             "pending_analyze": req_pending_analyze,
                             "analyzed": req_analyzed,
                             "processing": req_processing,
                             "prepared": req_prepared}}
