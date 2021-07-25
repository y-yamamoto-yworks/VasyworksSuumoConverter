"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
from common import SystemInfo
from converter.code_manager import CodeManager
from window import MainWindow


def main():
    """ エントリーポイント """
    # ディレクトリの準備
    prepare_directories()

    # メインWindowのオープン
    open_main_window()

    return


def prepare_directories():
    """ ディレクトリの準備 """
    # データ出力用ディレクトリ
    if not os.path.isdir(SystemInfo.get_instance().output_dir):
        os.makedirs(SystemInfo.get_instance().output_dir)

    # ログ用ディレクトリ
    if not os.path.isdir(SystemInfo.get_instance().log_dir):
        os.makedirs(SystemInfo.get_instance().log_dir)

    # 画像収集ログ用ディレクトリ
    if not os.path.isdir(SystemInfo.get_instance().image_log_dir):
        os.makedirs(SystemInfo.get_instance().image_log_dir)

    # パノラマ収集ログ用ディレクトリ
    if not os.path.isdir(SystemInfo.get_instance().panorama_log_dir):
        os.makedirs(SystemInfo.get_instance().panorama_log_dir)


def open_main_window():
    """ メインWindowのオープン """
    # Windowのオープン
    window = MainWindow()
    window.open()

    # WindowのClose後の処理
    del window

    # シングルトンの後処理
    SystemInfo.destroy_instance()
    CodeManager.destroy_instance()

    return


if __name__ == '__main__':
    main()
