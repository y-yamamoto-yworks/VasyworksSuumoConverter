"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""


def xstr(value):
    """ 文字列型に変換"""

    if value is None:
        return ""
    else:
        return str(value)


def xint(value):
    """ 整数型に変換 """

    if value is None:
        return 0
    else:
        try:
            return int(value)
        except:
            return 0


def xfloat(value):
    """ 浮動小数点型に変換 """

    if value is None:
        return float(0)
    else:
        try:
            return float(value)
        except:
            return float(0)


def int_to_bool(value):
    """ 整数型をブール型に変換"""

    if xint(value) == 0:
        return False
    else:
        return True


def float_normalize(value: float):
    """小数点以下の最後の0を取り除く"""
    ans = None
    value_str = xstr(value)
    parts = value_str.split('.')
    if len(parts) == 1:
        ans = parts[0]
    elif len(parts) == 2:
        left_part = parts[0]
        right_part = parts[1]
        while right_part[-1:] == '0' and len(right_part) > 0:
            right_part = right_part[:-1]

        ans = left_part
        if right_part != '':
            ans += '.{0}'.format(right_part)

    return ans

def comma_format(value: int):
    """ 数値を3桁カンマ区切りの書式にする"""
    return '{:,}'.format(value)
