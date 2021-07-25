"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import json
import urllib.request
import urllib.parse


class Api:
    """Apiの操作クラス"""
    @staticmethod
    def get_json_data(url):
        """ 指定したURLよりJSONデータを取得 """
        try:
            res = urllib.request.urlopen(url)

            res_data = res.read().decode('utf8')
            res_data = res_data.replace('&apos;', '\'').replace('&amp;', '&').replace('￥￥n', '\\n')
            ans = json.loads(res_data)
            res.close()
            return ans
        except:
            return None
