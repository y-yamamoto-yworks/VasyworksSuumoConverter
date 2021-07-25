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


class ImageSet(AppObject):
    """
    各部屋の画像セット
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()

        self.layout_image = None
        self.main_building_image = None
        self.perspective_image = None
        self.main_room_image = None
        self.surrounding_image = None
        self.environment_images = []
        self.room_images = []
        self.building_images = []

        self.base_images = []
        self.addition_images = []


        if room:
            self.building_id = room['building']['id']
            self.room_id = room['id']

            room_images = []
            room_images += room.get('pictures')
            building_images = []
            building_images += room['building'].get('pictures')

            # 間取図
            for image in room_images:
                if image['picture_type']['is_layout']:
                    self.layout_image = image
                    room_images.remove(image)
                    break

            # メイン建物外観
            for image in room_images:
                if image['picture_type']['id'] == 1010:
                    self.main_building_image = image
                    room_images.remove(image)
                    break
            if not self.main_building_image:
                for image in building_images:
                    if image['picture_type']['id'] == 1010:
                        self.main_building_image = image
                        building_images.remove(image)
                        break

            # 外観パース
            for image in room_images:
                if image['picture_type']['id'] == 1020:
                    self.perspective_image = image
                    room_images.remove(image)
                    break
            if not self.perspective_image:
                for image in building_images:
                    if image['picture_type']['id'] == 1020:
                        self.perspective_image = image
                        building_images.remove(image)
                        break

            # メイン室内内観
            for image in room_images:
                if image['picture_type']['id'] in (2020, 2030, 2040, ):
                    self.main_room_image = image
                    room_images.remove(image)
                    break

            # 周辺画像
            for image in room_images:
                if image['picture_type']['id'] == 1090:
                    self.surrounding_image = image
                    room_images.remove(image)
                    break
            if not self.surrounding_image:
                for image in building_images:
                    if image['picture_type']['id'] == 1090:
                        self.surrounding_image = image
                        building_images.remove(image)
                        break

            # 周辺環境画像
            for image in room_images:
                if image['picture_type']['id'] in (1090, 1100,):
                    self.environment_images += [image, ]
                    room_images.remove(image)
            for image in building_images:
                if image['picture_type']['id'] in (1090, 1100,):
                    self.environment_images += [image, ]
                    room_images.remove(image)

            # 部屋画像
            self.room_images += room_images

            # 建物画像
            self.building_images += building_images

        return

    def get_filename(self, file_type: str):
        """ 対象画像タイプのファイル名の取得 """
        ans = ''
        if file_type:
            ans = '{0}{1}.jpg'.format(
                self.room_id,
                CodeManager.get_instance().picture_file_types[file_type],
            )

        return ans

    def collect_jpeg(self, image, file_type):
        """JPEGファイルの収集"""
        filename = self.get_filename(file_type)
        if image and filename:
            DataHelper.download_jpeg(
                image[SystemInfo.get_instance().download_image_url],
                filename,
                self.building_id,
                self.room_id,
                SystemInfo.get_instance().image_dir,
                SystemInfo.get_instance().image_log_dir,
            )

    """
    画像収集
    """
    def collect(self):
        """ 送信対象ファイルを収集 """
        self.collect_layout()
        self.collect_exterior()
        self.collect_perspective()
        self.collect_interior()
        self.collect_surrounding()
        self.collect_base()
        self.collect_addition()
        self.collect_environment()

    def collect_layout(self):
        """ 間取図ファイルを収集 """
        if self.layout_image:
            self.collect_jpeg(
                self.layout_image,
                'Layout',
            )

    def collect_exterior(self):
        """ 外観画像ファイルを収集 """
        if self.main_building_image:
            self.collect_jpeg(
                self.main_building_image,
                'Exterior',
            )

    def collect_perspective(self):
        """ 外観パース画像ファイルを収集 """
        if self.perspective_image:
            self.collect_jpeg(
                self.perspective_image,
                'Perspective',
            )

    def collect_interior(self):
        """ 内覧画像ファイルを収集 """
        if self.main_room_image:
            self.collect_jpeg(
                self.main_room_image,
                'Interior',
            )

    def collect_base(self):
        """ ネット基本画像ファイルを収集 """
        for i in range(1, 4):
            file_type = 'Base{0}'.format(i)

            image = None
            if len(self.room_images) > 0:
                image = self.room_images.pop(0)
            elif len(self.building_images) > 0:
                image = self.building_images.pop(0)

            if image:
                self.base_images += [image, ]
                self.collect_jpeg(
                    image,
                    file_type,
                )

    def collect_addition(self):
        """ 追加画像ファイルを収集 """
        for i in range(1, 9):
            file_type = 'Addition{0}'.format(i)

            image = None
            if len(self.room_images) > 0:
                image = self.room_images.pop(0)
            elif len(self.building_images) > 0:
                image = self.building_images.pop(0)

            if image:
                self.addition_images += [image, ]
                self.collect_jpeg(
                    image,
                    file_type,
                )

    def collect_environment(self):
        """ 周辺環境画像ファイルを収集 """
        for i in range(1, 7):
            file_type = 'Environment{0}'.format(i)
            image = None
            if len(self.environment_images) > 0:
                image = self.environment_images.pop(0)

            if image:
                self.collect_jpeg(
                    image,
                    file_type,
                )

    def collect_surrounding(self):
        """ 周辺画像ファイルを収集 """
        if self.surrounding_image:
            self.collect_jpeg(
                self.surrounding_image,
                'Surrounding',
            )

    """
    画像情報
    """
    def get_main_building_comment(self):
        """ メイン建物外観コメント """
        ans = ''
        if self.main_building_image:
            ans = DataHelper.sanitize(xstr(self.main_building_image['comment']))

        return ans

    def get_perspective_comment(self):
        """ 外観パースコメント """
        ans = ''
        if self.perspective_image:
            ans = DataHelper.sanitize(xstr(self.perspective_image['comment']))

        return ans

    def get_main_room_category_code(self):
        """ メイン室内内観カテゴリ区分コード """
        ans = ''
        if self.main_room_image:
            id = xstr(self.main_room_image['picture_type']['id'])
            ans = xstr(CodeManager.get_instance().picture_types.get(id))

        return ans

    def get_main_room_comment(self):
        """ メイン室内内観コメント """
        ans = ''
        if self.main_room_image:
            ans = DataHelper.sanitize(xstr(self.main_room_image['comment']))

        return ans

    def get_base_category_code(self, index: int):
        """ ネット基本画像カテゴリ区分コード """
        ans = ''
        if 0 < index <= len(self.base_images):
            id = xstr(self.base_images[index - 1]['picture_type']['id'])
            ans = xstr(CodeManager.get_instance().picture_types.get(id))

        return ans

    def get_base_comment(self, index: int):
        """ ネット基本画像コメント """
        ans = ''
        if 0 < index <= len(self.base_images):
            ans = DataHelper.sanitize(xstr(self.base_images[index - 1]['comment']))

        return ans

    def get_addition_category_code(self, index: int):
        """ 追加画像カテゴリ区分コード """
        ans = ''
        if 0 < index <= len(self.addition_images):
            id = xstr(self.addition_images[index - 1]['picture_type']['id'])
            ans = xstr(CodeManager.get_instance().picture_types.get(id))

        return ans

    def get_addition_comment(self, index: int):
        """ 追加画像コメント """
        ans = ''
        if 0 < index <= len(self.addition_images):
            ans = DataHelper.sanitize(xstr(self.addition_images[index - 1]['comment']))

        return ans

