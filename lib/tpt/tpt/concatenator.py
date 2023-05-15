"""
TPTConcatenator module
"""
import codecs
import os
from tpt.file_manager import FolderTypeEnum
from tpt.model import TPTConcat


class TPTConcatenator:
    """
    TPTConcatenator class
    """
    def __init__(self, file_mngr, data, log, settings):
        self.file_mngr = file_mngr
        self.data = data
        self.log = log
        self.settings = settings

    def create_concatenated_file(self, request, file_type, ignore_binary=True):
        """
        Create concatenated file
        :param request:
        :param file_type:
        :param ignore_binary:
        :return:
        """
        file_out = self.file_mngr.get_concat_name (file_type)

        path_files = self.file_mngr.get_path_for_request(request, FolderTypeEnum.STORE_FILES)
        path_concats = self.file_mngr.get_path_for_request(request, FolderTypeEnum.STORE_CONCATS)

        path_file_out = os.path.join(path_concats, file_out)

        # Process files depending on the activity type
        compatible_extensions = self.file_mngr.get_compatible_extensions(file_type)

        files_to_concat = []

        # Prepare the list of files to concat
        for file in request.files:
            file_path = os.path.join(path_files, file.path)
            if compatible_extensions is None:
                if not ignore_binary or not self.file_mngr.is_binary_file(file_path):
                    files_to_concat.append(file_path)
            else:
                if os.path.splitext(file.path)[1] in compatible_extensions:
                    files_to_concat.append(file_path)

        # TODO: Return line start, end for each file in order to store it in the database for
        #  visualizations
        if len(files_to_concat) == 0:
            return None

        self.concatenate_files(files_to_concat, path_file_out)

        # Create TPTConcat object in the database
        idx = len(request.concats) + 1
        size = os.path.getsize(path_file_out)
        concat_data = TPTConcat(concat_id=idx, request_id=request.id, type=file_type, size=size)
        self.data.add_concat(concat_data)
        request.concats_additional_size = sum(c.size for c in request.concats)

        return concat_data

    def create_concatenated_statement(self, activity, ignore_binary=True):
        """
        Create concatenated statement
        :param activity:
        :param ignore_binary:
        :return:
        """

        file_out = 'statement.txt'
        path_statement = self.file_mngr.get_path_for_activity(activity)
        path_file_out = os.path.join(path_statement, file_out)
        files_to_concat = []

        # Prepare the list of files to concat
        for file in os.listdir(path_statement):
            file_path = os.path.join(path_statement, file)
            if not ignore_binary or not self.file_mngr.is_binary_file(file_path):
                files_to_concat.append(file_path)

        # TODO: Return line start, end for each file in order to store it in the database for
        #  visualizations

        self.concatenate_files(files_to_concat, path_file_out)

        for file in files_to_concat:
            os.remove(file)

    @staticmethod
    def concatenate_files(files, file_out):
        """
        Concatenate files
        :param files:
        :param file_out:
        :return:
        """
        # Ensure that destination path exists
        if not os.path.exists(os.path.dirname(file_out)):
            os.makedirs(os.path.dirname(file_out))

        # Concatenate files
        try:
            with codecs.open(file_out, mode='w') as outfile:
                for file in files:
                    with codecs.open(file, mode='r') as infile:
                        for line in infile:
                            outfile.write(line)
        except UnicodeDecodeError:
            pass