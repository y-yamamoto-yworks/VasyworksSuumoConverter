"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
import datetime
from urllib import request
from lib.convert import *
from common.app_object import AppObject
from common.system_info import SystemInfo
from .code_manager import CodeManager
from .data_helper import DataHelper


class PanoramaSet(AppObject):
    """
    各部屋のパノラマセット
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()

        self.room_panoramas = []
        self.building_panoramas = []

        self.panoramas = []

        if room:
            self.building_id = room['building']['id']
            self.room_id = room['id']

            # 部屋パノラマ
            self.room_panoramas += room.get('panoramas')

            # 建物パノラマ
            self.building_panoramas += room['building'].get('panoramas')

        return

    def get_filename(self, file_type: str):
        """ 対象画像タイプのファイル名の取得 """
        ans = ''
        if file_type:
            ans = '{0}{1}.jpg'.format(
                self.room_id,
                CodeManager.get_instance().panorama_file_types[file_type],
            )

        return ans

    def collect_jpeg(self, panorama, file_type):
        """JPEGファイルの収集"""
        filename = self.get_filename(file_type)
        if panorama and filename:
            DataHelper.download_jpeg(
                panorama['file_url'],
                filename,
                self.building_id,
                self.room_id,
                SystemInfo.get_instance().panorama_dir,
                SystemInfo.get_instance().panorama_log_dir,
            )

    """
    パノラマ収集
    """
    def collect(self):
        """ 送信対象ファイルを収集 """
        for i in range(1, 6):
            file_type = 'Scene{0}'.format(i)

            panorama = None
            if len(self.room_panoramas) > 0:
                panorama = self.room_panoramas.pop(0)
            elif len(self.building_panoramas) > 0:
                panorama = self.building_panoramas.pop(0)

            if panorama:
                self.panoramas += [panorama, ]
                self.collect_jpeg(
                    panorama,
                    file_type,
                )

    """
    パノラマ情報
    """
    @property
    def is_exist(self):
        """ パノラマがある場合は1、なければ0 """
        ans = '0'
        if len(self.panoramas) > 0:
            ans = '1'

        return ans

    def get_panorama_category_code(self, index: int):
        """ 追加画像カテゴリ区分コード """
        ans = ''
        if 0 < index <= len(self.panoramas):
            id = xstr(self.panoramas[index - 1]['picture_type']['id'])
            ans = xstr(CodeManager.get_instance().panorama_types.get(id))

        return ans

    def get_panorama_comment(self, index: int):
        """ パノラマコメント """
        ans = ''
        if 0 < index <= len(self.panoramas):
            ans = DataHelper.sanitize(xstr(self.panoramas[index - 1]['comment']))

        return ans
