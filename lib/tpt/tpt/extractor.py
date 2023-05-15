"""
TPTExtractor module
"""
import base64
import json
import os
import zipfile
from shutil import copyfile
from tpt.commons import ReqStatusEnum, TPTException
from tpt.file_manager import FolderTypeEnum
from tpt.model import TPTFile
from tpt.statistics import TPTStatisticsHelper


class TPTExtractor:
    """
    TPTExtractor class
    """
    def __init__(self, file_mngr, data, log, settings):
        self.file_mngr = file_mngr
        self.data = data
        self.log = log
        self.settings = settings

        self.statistics = TPTStatisticsHelper(self.data, self.settings)

    def save_data_request(self, request, data):
        """
        Save data request in tmp folder
        :param request:
        :param data:
        :return:
        """
        src_path = self.file_mngr.get_path_for_request(request, FolderTypeEnum.TEMP_SOURCE)
        ext_path = self.file_mngr.get_path_for_request(request, FolderTypeEnum.TEMP_EXTRACTED)
        files_path = self.file_mngr.get_path_for_request(request, FolderTypeEnum.STORE_FILES)

        # Ensure that destination paths exist
        try:
            if not os.path.exists(src_path):
                os.makedirs(src_path)
            if not os.path.exists(ext_path):
                os.makedirs(ext_path)
            if not os.path.exists(files_path):
                os.makedirs(files_path)
        except PermissionError as exc:
            request.status = ReqStatusEnum.PERMISSION_ERROR
            request.files_size = 0
            self.data.add_or_update_request(request)
            return False

        # format: filename:<file>,data:<mime_type>;base64,<data64>
        try:
            parts = data.split(';')
            data_sample = base64.b64decode(parts[1].split(',')[1])
            filename = parts[0].split(',')[0].split(':')[1]
            path = "{}_{}".format(request.id, filename)

            with open(os.path.join(src_path, os.path.basename(path)), 'wb') as file:
                file.write(data_sample)
        except IndexError:
            # Format of the request is not correct.
            request.status = ReqStatusEnum.ERROR
            request.files_size = 0
            self.data.add_or_update_request(request)
            return False

        return path

    def process(self, request):
        """
        Execute extraction process
        :param request:
        :param path:
        :return:
        """

        src_path = self.file_mngr.get_path_for_request(request, FolderTypeEnum.TEMP_SOURCE)
        ext_path = self.file_mngr.get_path_for_request(request, FolderTypeEnum.TEMP_EXTRACTED)
        files_path = self.file_mngr.get_path_for_request(request, FolderTypeEnum.STORE_FILES)

        # Extract the files in the output folder
        try:
            path = request.path
            cpy_src = os.path.join(src_path, os.path.basename(path))
            dst_src = os.path.join(ext_path, os.path.basename(path))
            copyfile(cpy_src, dst_src)
        except TypeError:
            return False

        max_depth = -1
        if request.activity.config is not None:
            config = json.loads(request.activity.config)
            if 'max_depth' in config:
                max_depth = int(config.max_depth)
        self.extract_file(os.path.join(ext_path, os.path.basename(path)), ext_path, max_depth)

        # Process the request files
        files = self.file_mngr.get_files(ext_path)

        total_size = 0

        # Prepare and store the files of this request
        for idx, file in enumerate(files):
            # prepare_file can modify the name of the file (adding a .txt extension for example)
            file_path = self.prepare_file(os.path.join(ext_path, file), files_path, file)
            file_path = file_path.replace('\\', '/')
            size = os.path.getsize(os.path.join(files_path, file_path))
            tpt_file = TPTFile(file_id=idx, request_id=request.id, path=file_path, size=size)

            self.data.add_file(tpt_file)
            total_size = total_size + size

        # Update request state in the TPT database
        if total_size == 0:
            # request has not any data to analyze
            request.status = ReqStatusEnum.ERROR
        else:
            request.status = ReqStatusEnum.PREPARED

        request.files_size = total_size
        self.data.add_or_update_request(request)

        if request.status == ReqStatusEnum.ERROR:
            return False

        return True

    def process_statement(self, activity, data=None, path=None):
        """
        Process statement
        :param activity:
        :param data:
        :param path:
        :return:
        """

        ext_path = self.file_mngr.get_path_for_activity(activity)

        # Ensure that destination paths exist
        if not os.path.exists(ext_path):
            os.makedirs(ext_path)

        if data is not None:
            try:
                parts = data.split(';')
                data_sample = base64.b64decode(parts[1].split(',')[1])
                filename = parts[0].split(',')[0].split(':')[1]
                path = "aux_{}_{}".format(activity.activity_id, filename)

                with open(os.path.join(ext_path, os.path.basename(path)), 'wb') as file:
                    file.write(data_sample)
            except IndexError:
                raise TPTException("Data is not in correct format")
        else:
            # Copy the original file in the path
            copyfile(path, os.path.join(ext_path, os.path.basename(path)))

        self.extract_file(os.path.join(ext_path, os.path.basename(path)), ext_path, -1)

        # Process the activity files
        files = self.file_mngr.get_files(ext_path)

        # Prepare and store the files of this activity
        for idx, file in enumerate(files):
            # prepare_file can modify the name of the file (adding a .txt extension for example)
            self.prepare_file(os.path.join(ext_path, file), ext_path, file)
            os.remove(os.path.join(ext_path, file))

    def extract_file(self, file_name, destination_path, max_level=1):
        """
        Recursively extract the files in the provided file
        :param file_name:
        :param destination_path:
        :param max_level:
        :return:
        """

        if max_level == 0:
            return

        # Process the file depending on the extension
        ext_files = []
        if file_name.endswith(".zip"):
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)
            with zipfile.ZipFile(file_name) as file_zip:
                for file_list in file_zip.filelist:
                    file_zip.extract(file_list, destination_path)
                    ext_files.append(os.path.join(destination_path, file_list.filename))
                file_zip.close()
        elif file_name.endswith(".gz"):
            # We cannot extract this file, just do nothing
            return
        elif file_name.endswith(".tar.gz"):
            # We cannot extract this file, just do nothing
            return
        elif file_name.endswith(".rar"):
            # We cannot extract this file, just do nothing
            return
        else:
            # We cannot extract this file, just do nothing
            return

        # For each extracted file, call recursively
        for ext_file in ext_files:
            out_path = os.path.join(destination_path, os.path.basename(ext_file).
                                    replace('.', '__'), '')
            self.extract_file(ext_file, out_path, max_level - 1)

        # Once the file has been extracted, just remove it
        os.remove(file_name)

    def prepare_file(self, file_in, file_out_path, file_relative_path):
        """
        Prepare file
        :param file_in:
        :param file_out_path:
        :param file_relative_path:
        :return:
        """

        file_out = os.path.join(file_out_path, file_relative_path)

        # Ensure that destination path exists
        if not os.path.exists(os.path.dirname(file_out)):
            os.makedirs(os.path.dirname(file_out))

        text = self.file_mngr.get_text_from_file(file_in)

        if text is None and file_in != file_out:
            copyfile(file_in, file_out)
        else:

            # add .txt extension to ensure the file is text (without loosing previous extension)
            file_out = file_out + '.txt'
            file_relative_path = file_relative_path + '.txt'

            self.log.debug('file_in: {}'.format(file_in))
            self.log.debug('file_out: {}'.format(file_out))

            with open(file_out, mode="wb") as file:
                file.write(text)

        return file_relative_path
