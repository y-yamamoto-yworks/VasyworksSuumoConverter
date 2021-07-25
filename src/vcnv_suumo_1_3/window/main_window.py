"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import tkinter
import time
from tkinter import messagebox, ttk
from common import SystemInfo, WindowBase
from converter import Converter


class MainWindow(WindowBase):
    """
    メインWindow
    """
    form = None
    progress = None
    progressbar = None
    button_go = None

    def __init__(self):
        """ コンストラクタ """
        super().__init__()

        # 画面の設定
        self.width = 640
        self.height = 160
        self.form.title(SystemInfo.get_instance().app_title)
        self.form.columnconfigure(1, weight=True)

        # 利用API表示
        lbl_api_title = tkinter.Label(
            self.form,
            text='API:',
        )
        lbl_api_title.grid(row=0, column=0, padx=5, pady=5,)
        ctl_api = tkinter.Entry(
            self.form,
        )
        ctl_api.insert(0, SystemInfo.get_instance().api_url)
        ctl_api.configure(state='readonly')
        ctl_api.grid(row=0, column=1, padx=5, pady=5, sticky=tkinter.EW,)

        # 出力先表示
        lbl_output_title = tkinter.Label(
            self.form,
            text='出力:',
        )
        lbl_output_title.grid(row=1, column=0, padx=5, pady=5,)
        ctl_output = tkinter.Entry(
            self.form,
        )
        ctl_output.insert(0, SystemInfo.get_instance().output_dir)
        ctl_output.configure(state='readonly')
        ctl_output.grid(row=1, column=1, padx=5, pady=5, sticky=tkinter.EW,)

        # 進捗状況
        lbl_progress_title = tkinter.Label(
            self.form,
            text='実行状況:',
        )
        lbl_progress_title.grid(row=2, rowspan=2, column=0,)
        lbl_progress = tkinter.Label(
            self.form,
            text='【未実行】',
        )
        lbl_progress.grid(row=2, column=1, ipadx=10, sticky=tkinter.W)
        self.progress = lbl_progress
        ctl_progress = ttk.Progressbar(
            self.form,
            orient=tkinter.HORIZONTAL,
            mode='determinate',
        )
        ctl_progress.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tkinter.EW,)
        self.progressbar = ctl_progress

        # 実行ボタン
        cmd_go = tkinter.Button(
            self.form,
            text='実行',
            command=lambda: self.cmd_go_click(),
        )
        cmd_go.grid(row=4, column=0, columnspan=2,)
        self.button_go = cmd_go

        return

    def __del__(self):
        """ デストラクタ """
        super().__del__()

        self.status = None
        self.progressbar = None

        return

    def cmd_go_click(self):
        """ 実行ボタンのクリック """
        try:
            ask_message = '処理を実行します。\n実行すると前回の送信データや画像はクリアされます。'
            if messagebox.askokcancel(title='コンバートの実行', message=ask_message, default='cancel'):
                self.form.configure(cursor='wait')

                self.convert()

                self.form.configure(cursor='arrow')
                self.button_go.configure(state=tkinter.DISABLED)
                messagebox.showinfo(SystemInfo.get_instance().app_title, '処理が終了しました。')
            return

        except Exception as e:
            self.form.configure(cursor='arrow')
            messagebox.showerror(SystemInfo.get_instance().app_title, '処理に失敗しました。\n\n{0}'.format(e.args))
            return

    def convert(self):
        """コンバートの実行"""
        converter = None
        try:
            converter = Converter()
            converter.progress = self.progress
            converter.progressbar = self.progressbar

            converter.convert()

            return

        except:
            if converter:
                del converter
            raise
