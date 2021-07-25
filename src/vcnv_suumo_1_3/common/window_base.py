"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import tkinter
from .app_object import AppObject


class WindowBase(AppObject):
    """
    Windowのベースクラス
    """
    form = None
    width = 300
    height = 200

    def __init__(self):
        """ コンストラクタ """
        super().__init__()

        self.form = tkinter.Tk()
        return

    def __del__(self):
        """ デストラクタ """
        if self.is_disposable:
            self.dispose()

        super().__del__()
        return

    def dispose(self):
        """ Windowの廃棄 """
        del self.form
        self.form = None

        super().dispose()
        return

    def open(self, centering=True):
        """ Windowのオープン """
        if centering:
            # Windowのセンタリング
            top = int((self.form.winfo_screenwidth() - self.width) / 2)
            left = int((self.form.winfo_screenheight() - self.height) / 2)

            self.form.geometry(u'{width:d}x{height:d}+{top:d}+{left:d}'.format(
                width=self.width,
                height=self.height,
                top=top,
                left=left,
            ))

        self.form.mainloop()
        return
