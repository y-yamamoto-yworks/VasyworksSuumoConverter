"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
import shutil
import zipfile
import math
from dateutil import relativedelta
from pyproj import Transformer
from urllib import request
from lib.convert import *
from .code_manager import CodeManager


class DataHelper:
    """データ加工用ヘルパークラス"""
    @classmethod
    def sanitize(cls, data: str):
        """ 文字列のサニタイジング """
        ans = data

        ans = ans.replace('"', '”')
        ans = ans.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
        ans = ans.replace('\t', ' ')

        ans = ans.replace('%', '％').replace('･', '・')
        ans = ans.replace('%', '％').replace('･', '・')
        ans = ans.replace('【', '（').replace('】', '）')
        ans = ans.replace('(', '（').replace(')', '）')

        ans = ans.replace('Ⅰ', 'I').replace('Ⅱ', 'II').replace('Ⅲ', 'III')
        ans = ans.replace('Ⅳ', 'IV').replace('Ⅴ', 'V').replace('Ⅵ', 'VI')
        ans = ans.replace('Ⅶ', 'VII').replace('Ⅷ', 'VIII').replace('Ⅸ', 'IX')
        ans = ans.replace('Ⅹ', 'X')
        ans = ans.replace('髙', '高').replace('﨑', '崎')

        return ans

    @classmethod
    def get_url_filename(cls, url: str):
        """ URLからファイル名を取得 """
        ans = None
        if url:
            ans = url.rsplit('/', 1)[1]
        return ans

    """
    JPEGファイルのダウンロード
    """
    @classmethod
    def download_jpeg(cls, url, filename, building_id, room_id, collection_dir, log_dir):
        """  JPEGファイルのダウンロード """
        if not url or not filename or not building_id or not room_id or not collection_dir or not log_dir:
            return False

        file_id, ext = os.path.splitext(DataHelper.get_url_filename(url))
        if ext.lower() not in ('.jpg', '.jpeg'):
            # JPEGファイル以外ならFalse
            return False

        log_file_dir = os.path.join(
            log_dir,
            '{0}/'.format(building_id).replace('/', os.sep),
            '{0}/'.format(room_id).replace('/', os.sep),
            '{0}/'.format(file_id).replace('/', os.sep),
        )
        log_file_path = os.path.join(log_file_dir, filename)

        if not os.path.exists(log_file_path):
            # 過去に送信した履歴がない場合のみ収集処理

            if os.path.isdir(log_file_dir):
                # ディレクトリはあるがファイル名が違う場合は一旦ディレクトリごと削除
                shutil.rmtree(log_file_dir)
            os.makedirs(log_file_dir)

            file = None
            jpeg = None
            try:
                jpeg = request.urlopen(url).read()
                file_path = os.path.join(collection_dir, filename)

                if not os.path.exists(file_path):
                    # 送信対象ディレクトリにファイルがない場合
                    file = open(file_path, mode='wb')
                    file.write(jpeg)
                    file.close()

                file = open(log_file_path, mode='wb')
                file.write(jpeg)
                file.close()

                del jpeg
                ans = True

            except:
                if file:
                    if not file.closed:
                        file.close()
                if jpeg:
                    del jpeg

        return True

    """
    ファイルの削除
    """
    @classmethod
    def remove_file(cls, file_path: str):
        if os.path.exists(file_path):
            os.remove(file_path)

    """
    ディレクトリの再作成
    """
    @classmethod
    def remake_dir(cls, file_path: str):
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        os.makedirs(file_path)

    """
    画像ZIPファイルの作成
    """
    @classmethod
    def make_image_zip(cls, file_path: str, data_dir: str):
        zip_file = None
        try:
            zip_file = None

            for file_name in os.listdir(data_dir):
                file_id, ext = os.path.splitext(file_name)
                if ext.lower() in ('.jpg', '.jpeg'):
                    if zip_file is None:
                        zip_file = zipfile.ZipFile(
                            file=file_path,
                            mode='w',
                            compression=zipfile.ZIP_DEFLATED, )
                    zip_file.write(
                        filename=os.path.join(data_dir, file_name),
                        arcname=file_name,
                    )

            if zip_file:
                zip_file.close()

        except:
            if zip_file:
                zip_file.close()
            raise Exception('ZIPファイルの作成に失敗しました。')

    """
    緯度経度
    """
    @classmethod
    def get_jp_lat_lng(cls, w_lat: float, w_lng: float):
        """ 緯度経度（日本測地系） """
        t_lng = 0
        t_lat = 0
        if w_lat > 0 and w_lng > 0:
            transformer = Transformer.from_crs(4326, 4301, always_xy=True)
            t_lng, t_lat = transformer.transform(w_lng, w_lat)
            del transformer

        return t_lat, t_lng
