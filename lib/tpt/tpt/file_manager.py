"""
TPT File Manager module
"""

import mimetypes
import os
import shutil
import zipfile
import docx
import textract
from textract.exceptions import CommandLineError
from tpt.commons import CmpTypeEnum, FolderTypeEnum
from tpt.model import TPTFile, TPTConcat


class TPTFileManager:
    """
    TPT File Manager classs
    """
    def __init__(self, log, settings):
        self.log = log
        self.settings = settings

        # TODO: add more extensions
        self.extensions = {
            CmpTypeEnum.TEXT: None,
            CmpTypeEnum.TEXT_ONLY: [".txt", ".csv", ".docx", ".doc", ".pdf", ".html", ".htm"],
            CmpTypeEnum.C: [".c", ".h", ".xml"],
            CmpTypeEnum.CPP: [".cpp", ".c", ".h", ".hpp", ".xml"],
            CmpTypeEnum.JAVA: [".java", ".xml", ".jsp"],
        }

        try:
            self.tmp_path = os.path.abspath(self.settings.get('DataStorage', 'TmpPath'))
            self.store_path = os.path.abspath(self.settings.get('DataStorage', 'StorePath'))
        except ValueError:
            self.tmp_path = os.path.abspath('/app/store/tmp')
            self.store_path = os.path.abspath('/app/store/tpt')

        if not os.path.isdir(self.tmp_path):
            os.makedirs(self.tmp_path)

        if not os.path.isdir(self.store_path):
            os.makedirs(self.store_path)

    def get_path_for_request(self, request, folder_type):
        """
        Get path for request
        :param request:
        :param folder_type:
        :return:
        """
        if folder_type in (FolderTypeEnum.TEMP_SOURCE, FolderTypeEnum.TEMP_EXTRACTED):
            base = self.tmp_path
        else:
            base = self.store_path

        return os.path.join(base, str(request.activity_id), str(request.user_id), str(request.id),
                            folder_type.value)

    def delete_folders_for_request(self, request):
        """
        Delete folders for request
        :param request:
        :return:
        """
        shutil.rmtree(os.path.join(self.tmp_path, str(request.activity_id), str(request.user_id),
                                   str(request.id)))

        shutil.rmtree(os.path.join(self.store_path, str(request.activity_id), str(request.user_id),
                                   str(request.id)))

    def delete_folders_for_activity_and_user_id(self, activity_id, user_id):
        """
        Delete folders for activity and user
        :param activity_id:
        :param user_id:
        :return:
        """
        path = os.path.join(self.tmp_path, str(activity_id), str(user_id))

        if os.path.exists(path):
            shutil.rmtree(path)

        path = os.path.join(self.store_path, str(activity_id), str(user_id))

        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except PermissionError:
                pass

    def delete_folders_for_activity(self, activity_id):
        """
        Delete folders for activity
        :param activity_id:
        :return:
        """
        path = os.path.join(self.tmp_path, str(activity_id))

        if os.path.exists(path):
            shutil.rmtree(path)

        path = os.path.join(self.store_path, str(activity_id))

        if os.path.exists(path):
            try:
                shutil.rmtree(path)
            except PermissionError:
                pass

    def get_path_for_activity(self, activity):
        """
        Get path for activity
        :param activity:
        :return:
        """
        base = self.store_path

        return os.path.join(base, str(activity.activity_id), 'statement')

    def get_path_for_file(self, file):
        """
        Get path for file
        :param file:
        :return:
        """
        path = None
        if isinstance(file, TPTFile):
            path = os.path.join(self.get_path_for_request(file.request,
                                                          FolderTypeEnum.STORE_FILES), file.path)

        elif isinstance(file, TPTConcat):
            path = os.path.join(self.get_path_for_request(file.request,
                                                          FolderTypeEnum.STORE_CONCATS),
                                self.get_concat_name(file.type))

        return path

    def get_path_for_file_request(self, file, request):
        """
        Get path for file request
        :param file:
        :param request:
        :return:
        """
        path = None
        if isinstance(file, TPTFile):
            path = os.path.join(self.get_path_for_request(request, FolderTypeEnum.STORE_FILES),
                                file.path)

        elif isinstance(file, TPTConcat):
            path = os.path.join(self.get_path_for_request(request, FolderTypeEnum.STORE_CONCATS),
                                self.get_concat_name(file.type))

        return path

    @staticmethod
    def get_concat_name(concat_type):
        """
        Get concat name
        :param concat_type:
        :return:
        """
        return 'concat.' + concat_type.value

    def get_compatible_extensions(self, concat_type):
        """
        Get compatible extension
        :param concat_type:
        :return:
        """
        return self.extensions[concat_type]

    def get_files(self, path, extensions=None):
        """
        Get files from path
        :param path:
        :param extensions:
        :return:
        """
        files = []

        for file in os.listdir(path):
            fpa = os.path.join(path, file)
            if os.path.isdir(fpa):
                for afn in self.get_files(fpa, extensions):
                    files.append(os.path.join(file, afn))
            elif extensions is None or os.path.splitext(fpa)[1] in extensions:
                files.append(file)
        return files

    @staticmethod
    def get_text_from_docx(filename):
        """
        Get text form docx
        :param filename:
        :return:
        """
        doc = docx.Document(filename)
        full_text = b''
        for paragraph in doc.paragraphs:
            full_text += b' \n'+paragraph.text.encode()
        # return '\n'.join(full_text)
        return full_text

    @staticmethod
    def get_text_from_pdf(filename):
        """
        Get text form pdf
        :param filename:
        :return:
        """
        text = textract.process(filename)
        return text

    @staticmethod
    def get_text_from_pdf_ocr(filename, language):
        """
        Get text from pdf ocr
        :param filename:
        :param language:
        :return:
        """
        text = textract.process(filename, method='tesseract', language=language)
        return text

    @staticmethod
    def get_text_from_plain_text(filename):
        """
        Get text form pdf
        :param filename:
        :return:
        """
        with open(filename, mode='rb') as file:
            return file.read()

    def get_text_from_file(self, file):
        """
        Get text from file
        :param file:
        :return:
        """
        text = None
        try:
            # Process the file depending on the extension
            if file.endswith(".pdf"):
                text = self.get_text_from_pdf(file)
            elif file.endswith(".docx"):
                text = self.get_text_from_docx(file)
            else:
                text = self.get_text_from_plain_text(file)
        except CommandLineError:
            pass

        return text

    @staticmethod
    def unzip_file(filename, folder):
        """
        Unzip file
        :param filename:
        :param folder:
        :return:
        """
        with zipfile.ZipFile(filename) as file_zip:
            file_zip.extractall(folder)
            file_zip.close()

    @staticmethod
    def is_binary_file(file_path):
        """
        Check if file is binary
        :param file_path:
        :return:
        """
        # TODO: determine a better way to find if the file is binary or not
        mime = mimetypes.guess_type(file_path)
        return mime is None or mime[0] is None or not mime[0].startswith("text")

    def get_file_types(self, file_path):
        """
        Get file types
        :param file_path:
        :return:
        """
        file_types = []

        if not self.is_binary_file(file_path):
            file_types.append(CmpTypeEnum.TEXT)
            extension = os.path.splitext(file_path)[1]

            for cmp_type in self.extensions:
                if cmp_type != CmpTypeEnum.TEXT and extension in self.extensions[cmp_type]:
                    file_types.append(cmp_type)
        return file_types
