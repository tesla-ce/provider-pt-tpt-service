import base64
import unittest
import shutil
import configparser
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import SingletonThreadPool
from tpt import TPT
from tpt import model


class UtilHelper(unittest.TestCase):
    engine = None

    def setUp(self):
        # Settings object
        self.settings_file = 'tpt/tests/tpt_test.ini'
        self.settings = configparser.ConfigParser()
        self.settings.read(self.settings_file)
        self.settings._interpolation = configparser.ExtendedInterpolation()

        # clear directories
        store_path = os.path.abspath(self.settings.get('DataStorage', 'StorePath'))
        tmp_path = os.path.abspath(self.settings.get('DataStorage', 'TmpPath'))

        try:
            shutil.rmtree(store_path)
        except FileNotFoundError:
            pass

        try:
            shutil.rmtree(tmp_path)
        except FileNotFoundError:
            pass

        self.tpt = None
        execution_options = {"schema_translate_map": {"tpt": None}}
        connect_args = {}

        self.sqlite_name = "sqlite:///tpt.db"
        '''
        db_address = os.getenv('DB_ADDRESS', 'localhost')
        db_port = os.getenv('DB_PORT', 55432)
        db_name = os.getenv('DB_NAME', 'tpt_database')
        db_user = os.getenv('DB_USER', 'tpt_admin')
        db_password = os.getenv('DB_PASSWORD', 'tpt_admin')
        db_engine = os.getenv('DB_ENGINE', 'postgresql+psycopg2')

        self.sqlite_name = u'{0}://{1}:{2}@{3}:{4}/{5}'.format(db_engine, db_user, db_password,
                                                               db_address, db_port, db_name)
        '''
        self.engine = create_engine(self.sqlite_name, execution_options=execution_options,
                                    connect_args=connect_args, poolclass=SingletonThreadPool,
                                    echo_pool='debug', echo=True, pool_recycle=3600)

        model.BASE.metadata.drop_all(self.engine)
        self.tpt = TPT(engine=self.engine, settings_file=self.settings_file, logger=None,
                       create_db=True, debug=True)

    def tearDown(self):
        del self.tpt

        if self.engine is not None:
            self.engine.dispose()

        #os.remove(self.sqlite_name.replace('sqlite:///', ''))

    def get_tpt(self):
        return self.tpt

    @staticmethod
    def get_sample_b64_from_content(content_b64, mime_type, filename):
        return "filename:{},data:{};base64,{}".format(filename, mime_type,
                                                      content_b64.decode('utf8'))

    def get_sample_b64_from_path(self, path, mime_type):
        # format: filename:<file>,data:<mime_type>;base64,<data64>
        file_out = os.path.abspath('./tpt/tests/documents/{}'.format(path))
        # with codecs.open(file_out, mode="rb", encoding='utf-8', errors='ignore') as file:
        with open(file_out, 'rb') as file:
            file_content = file.read()
            data_b64 = base64.b64encode(file_content)
            filename = path.split(os.path.sep)[-1]

            return self.get_sample_b64_from_content(data_b64, mime_type, filename)
