"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os


class AppObject:
    """ アプリケーション内オブジェクトのベースクラス """
    is_disposable = True

    def __del__(self):
        """ デストラクタ """
        if self.is_disposable:
            self.dispose()
        return

    def dispose(self):
        """ オブジェクトの廃棄 """
        self.is_disposable = False
        return

