"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
import configparser
from lib.convert import *


class SystemInfo:
    """
    システム情報
    """
    _instance = None

    def __init__(self):
        """ コンストラクタ """
        self.app_title = 'Homesコンバータ'

        # コンフィグ設定ファイルからの読み込み
        config_ini = configparser.ConfigParser()
        config_ini.read('config.ini', encoding='utf-8')

        self.api_url = config_ini.get('Application', 'Api_Url').format(
            key=config_ini.get('Application', 'Api_key')
        )
        self.download_image_url = config_ini.get('Application', 'Download_image_url')
        self.tax_rate = xfloat(config_ini.get('Application', 'Tax_rate'))

        self.csv_version = config_ini.get('Suumo', 'Csv_version')
        self.company_code = config_ini.get('Suumo', 'Company_code')
        self.branch_code = config_ini.get('Suumo', 'Branch_code')

        del config_ini

        # その他
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        home_dir = os.environ.get('HOME')
        if not home_dir:
            home_dir = os.getenv('HOMEDRIVE') + os.getenv('HOMEPATH')
        data_dir = 'Documents/Convert/Suumo/{0}/'.format(self.csv_version).replace('/', os.sep)

        # データ出力用ディレクトリ
        self.output_dir = os.path.join(home_dir, data_dir)
        self.image_dir = os.path.join(self.output_dir, 'image/'.replace('/', os.sep))
        self.panorama_dir = os.path.join(self.output_dir, 'panorama/'.replace('/', os.sep))
        self.log_dir = os.path.join(self.output_dir, 'log/'.replace('/', os.sep))
        self.image_log_dir = os.path.join(self.log_dir, 'image/'.replace('/', os.sep))
        self.panorama_log_dir = os.path.join(self.log_dir, 'panorama/'.replace('/', os.sep))

        return

    @classmethod
    def get_instance(cls):
        """コンフィグ設定オブジェクトの生成"""
        if not cls._instance:
            cls._instance = SystemInfo()

        return cls._instance

    @classmethod
    def destroy_instance(cls):
        """ インスタンスの消去 """
        del cls._instance
        return
