"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import math
import datetime
from dateutil.relativedelta import relativedelta
from lib.convert import *
from common.app_object import AppObject
from common.system_info import SystemInfo
from .code_manager import CodeManager
from .data_helper import DataHelper
from .image_set import ImageSet
from .panorama_set import PanoramaSet


class RoomData(AppObject):
    """
    部屋データ
    """
    def __init__(self, room):
        """ コンストラクタ """
        super().__init__()
        self.room = None

        if room:
            self.room = room
            self.image_set = ImageSet(room)
            self.panorama_set = PanoramaSet(room)
        else:
            raise Exception("部屋データが不正です。")

        # 緯度経度（日本測地系）
        w_lat = xfloat(self.room['building']['lat'])    # 世界測地系（WGS84）緯度
        w_lng = xfloat(self.room['building']['lng'])    # 世界測地系（WGS84）経度
        self.jp_lat, self.jp_lng = DataHelper.get_jp_lat_lng(w_lat, w_lng) # 日本測地系に変換

        return

    def __del__(self):
        """ デストラクタ """
        if self.is_disposable:
            del self.image_set
            del self.panorama_set

        super().__del__()

        return

    """
    建物情報
    """
    @property
    def building_name(self):
        """ 建物名称 """
        ans = xstr(self.room['building']['building_name'])
        return DataHelper.sanitize(ans)

    @property
    def building_code(self):
        """ 建物コード """
        ans = xstr(self.room['building']['building_code'])
        return DataHelper.sanitize(ans)

    @property
    def building_floors(self):
        """ 建物階数（地上） """
        return xstr(self.room['building']['building_floors'])

    @property
    def building_undergrounds(self):
        """ 建物階数（地下） """
        ans = ''
        data = xint(self.room['building']['building_undergrounds'])
        if data > 0:
            ans = xstr(data)

        return ans

    @property
    def building_rooms(self):
        """ 総戸数 """
        return xstr(self.room['building']['building_rooms'])

    @property
    def building_type_code(self):
        """ 物件種別コード """
        id = xstr(self.room['building']['building_type']['id'])
        return xstr(CodeManager.get_instance().building_types.get(id))

    @property
    def structure_code(self):
        """ 構造コード """
        id = xstr(self.room['building']['structure']['id'])
        return xstr(CodeManager.get_instance().structures.get(id))

    @property
    def build_year(self):
        return xstr(self.room['building']['build_year'])

    @property
    def build_month(self):
        return '{0:0>2}'.format(xstr(self.room['building']['build_month']))

    def get_railway_code(self, index: int):
        """ 沿線コード """
        if index not in (1, 2, 3):
            return ''

        id = xstr(self.room['building']['station' + xstr(index)]['railway']['id'])
        return xstr(CodeManager.get_instance().railways.get(id))

    def get_station_code(self, index: int):
        """ 駅コード """
        if index not in (1, 2, 3):
            return ''

        id = xstr(self.room['building']['station' + xstr(index)]['id'])
        return xstr(CodeManager.get_instance().stations.get(id))

    def get_arrival_type_code(self, index: int):
        """ 到着種別コード """
        if index not in (1, 2, 3):
            return ''

        id = xstr(self.room['building']['arrival_type' + xstr(index)]['id'])
        return xstr(CodeManager.get_instance().arrival_types.get(id))

    def get_station_time(self, index: int):
        """ 駅までの所要時間 """
        if index not in (1, 2, 3):
            return ''

        ans = ''
        if xstr(self.room['building']['arrival_type' + xstr(index)]['id']) != '0':
            ans = xstr(self.room['building']['station_time' + xstr(index)])

        return ans

    def get_bus_stop(self, index: int):
        """ バス停名 """
        if index not in (1, 2, 3):
            return ''

        ans = ''
        if xstr(self.room['building']['arrival_type' + xstr(index)]['id']) == '2':   # バス利用
            ans = DataHelper.sanitize(xstr(self.room['building']['bus_stop' + xstr(index)]))

        return ans

    def get_bus_stop_time(self, index: int):
        """ バス停までの徒歩時間 """
        if index not in (1, 2, 3):
            return ''

        ans = ''
        if xstr(self.room['building']['arrival_type' + xstr(index)]['id']) == '2':   # バス利用
            ans = xstr(self.room['building']['bus_stop_time' + xstr(index)])

        return ans

    @property
    def address(self):
        """ 住所 """
        ans = ''
        if xint(self.room['building']['pref']['id']) != 0:
            ans += xstr(self.room['building']['pref']['name'])

        if xint(self.room['building']['city']['id']) != 0:
            ans += xstr(self.room['building']['city']['name'])

        if xstr(self.room['building']['town_name']) != '':
            ans += xstr(self.room['building']['town_name'])
        else:
            ans += xstr(self.room['building']['town_address'])

        return DataHelper.sanitize(ans)

    @property
    def house_no(self):
        """ 番地 """
        return DataHelper.sanitize(xstr(self.room['building']['house_no']))

    @property
    def building_no(self):
        """ 棟名 """
        return DataHelper.sanitize(xstr(self.room['building']['building_no']))

    @property
    def show_on_map(self):
        """ 地図表示フラグ """
        ans = '0'
        if self.jp_lat > 0 and self.jp_lng > 0:
            ans = '1'

        return ans

    @property
    def lat(self):
        """ 緯度（ミリ秒） """
        ans = ''
        if self.jp_lat > 0:
            ans = xstr(int(self.jp_lat * 3600000))

        return ans

    @property
    def lng(self):
        """ 経度（ミリ秒） """
        ans = ''
        if self.jp_lng > 0:
            ans = xstr(int(self.jp_lng * 3600000))

        return ans

    @property
    def garage_type_code(self):
        """ 駐車場種別コード """
        id = xstr(self.room['building']['garage_type']['id'])
        ans = xstr(CodeManager.get_instance().arrival_types.get(id))

        if id == 2:
            # 近隣確保の場合は距離と駐車料金は必須
            lower_fee = xint(self.room['building']['garage_fee_lower'])
            upper_fee = xint(self.room['building']['garage_fee_upper'])
            distance = xint(self.room['building']['garage_distance'])

            if lower_fee <= 0 and upper_fee <= 0:
                ans = '0'
            elif distance <= 0 or distance > 2000:
                ans = '0'

        return ans

    @property
    def garage_fee(self):
        """ 駐車料金"""
        ans = ''
        if self.garage_type_code in ('2', '3'):
            # 有料または近隣確保
            lower_fee = xint(self.room['building']['garage_fee_lower'])
            upper_fee = xint(self.room['building']['garage_fee_upper'])

            data = lower_fee
            if upper_fee > data:
                data = upper_fee

            if data > 0:
                if self.room['building']['garage_fee_tax_type']['is_excluding']:
                    data = int(data * (1 + SystemInfo.get_instance().tax_rate))

            ans = float_normalize(data / 10000)

        return ans

    @property
    def garage_distance(self):
        """ 近隣確保の駐車場距離 """
        ans = ''
        if self.garage_type_code == '3':
            data = xint(self.room['building']['garage_distance'])
            if 0 < data <= 2000:
                ans = xstr(data)

        return ans

    def get_facility_category(self, index: int):
        """ 周辺施設カテゴリ """
        if index < 1 or index > 6:
            return ''

        ans = ''
        if len(self.room['building']['facilities']) >= index:
            id = xstr(self.room['building']['facilities'][index - 1]['facility']['id'])
            ans = xstr(CodeManager.get_instance().get_instance().facilities.get(id))

        return ans

    def get_facility_name(self, index: int):
        """ 周辺施設名 """
        if index < 1 or index > 6:
            return ''

        ans = ''
        if len(self.room['building']['facilities']) >= index:
            if xstr(self.room['building']['facilities'][index - 1]['facility']['id']) != '0':
                ans = xstr(self.room['building']['facilities'][index - 1]['facility_name'])

        return ans

    def get_facility_distance(self, index: int):
        """ 周辺施設距離 """
        if index < 1 or index > 6:
            return ''

        ans = ''
        if len(self.room['building']['facilities']) >= index:
            if xstr(self.room['building']['facilities'][index - 1]['facility']['id']) != '0':
                ans = xstr(self.room['building']['facilities'][index - 1]['distance'])

        return ans

    """
    部屋情報
    """
    @property
    def room_id(self):
        """ 部屋ID """
        return xstr(self.room['id'])

    @property
    def room_no(self):
        """ 部屋番号 """
        ans = xstr(self.room['room_no'])
        return DataHelper.sanitize(ans)

    @property
    def room_floor(self):
        """ 部屋階数 """
        return xstr(self.room['room_floor'])

    @property
    def room_count(self):
        """ 間取り部屋数 """
        return xstr(self.room['layout_type']['room_count'])

    @property
    def layout_type_code(self):
        """ 間取種別コード """
        id = xstr(self.room['layout_type']['id'])
        return xstr(CodeManager.get_instance().layout_types.get(id))

    def get_western_style_room(self, index: int):
        """ 洋室間取詳細の帖数 """
        if index < 1 or index > 10:
            return ''

        ans = ''
        data = xfloat(self.room['western_style_room' + xstr(index)])
        if data > 0:
            ans = float_normalize(data)

        return ans

    def get_japanese_style_room(self, index: int):
        """ 和室間取詳細の帖数 """
        if index < 1 or index > 10:
            return ''

        ans = ''
        data = xfloat(self.room['japanese_style_room' + xstr(index)])
        if data > 0:
            ans = float_normalize(data)

        return ans

    @property
    def kitchen(self):
        """ キッチン間取詳細 """
        ans = ''
        for index in range(1, 4):
            notation = xstr(self.room['kitchen_type' + xstr(index)]['notation'])
            if notation != '':
                data = xfloat(self.room['kitchen' + xstr(index)])
                if data > 0:
                    ans += notation + float_normalize(data)

        return ans

    def get_store_room(self, index: int):
        """ 納戸間取詳細の帖数 """
        if index < 1 or index > 3:
            return ''

        ans = ''
        data = xfloat(self.room['store_room' + xstr(index)])
        if data > 0:
            ans = float_normalize(data)

        return ans

    def get_loft(self, index: int):
        """ ロフト間取詳細の帖数 """
        if index < 1 or index > 2:
            return ''

        ans = ''
        data = xfloat(self.room['loft' + xstr(index)])
        if data > 0:
            ans = float_normalize(data)

        return ans

    def get_sun_room(self, index: int):
        """ 納戸間取詳細の帖数 """
        if index < 1 or index > 2:
            return ''

        ans = ''
        data = xfloat(self.room['sun_room' + xstr(index)])
        if data > 0:
            ans = float_normalize(data)

        return ans

    @property
    def transaction_mode_code(self):
        """ 取引態様コード """
        ans = '4'       # 仲介先物
        if not self.room['building']['management_type']['is_condo_management']:
            # 分譲管理のマンションではない場合
            id = xstr(self.room['building']['management_type']['id'])
            ans = xstr(CodeManager.get_instance().management_transaction_modes.get(id))
        if self.room['is_condo_management']:
            # 分譲管理の部屋の場合
            ans = '3'       # 仲介元付

        return ans

    @property
    def rent(self):
        """ 賃料 """
        return float_normalize(xint(self.room['rent']) / 10000)

    @property
    def condo_fees(self):
        """ 共益費 """
        ans = ''

        id = xint(self.room['condo_fees_type']['id'])
        if id == 10:
            ans = float_normalize(xint(self.room['condo_fees']) / 10000)
        elif id in (20, 21):
            ans = '0'

        return ans

    @property
    def reikin(self):
        """ 礼金 """
        ans = '0'
        type_id = xint(self.room['key_money_type1']['id'])
        if type_id in (10, 11, 12):
            notation_id = xint(self.room['key_money_notation1']['id'])
            value = xstr(self.room['key_money_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2:
                ans = float_normalize(xfloat(value) / 10000)
            elif notation_id == 3:
                ans = float_normalize(xfloat(value))

        return ans

    @property
    def reikin_unit_code(self):
        """ 礼金単位区分コード """
        ans = ''
        type_id = xint(self.room['key_money_type1']['id'])
        value = xstr(self.room['key_money_value1'])
        if type_id in (10, 11, 12) and value != '0':
            notation_id = xint(self.room['key_money_notation1']['id'])
            if notation_id == 2:
                ans = '2'
            elif notation_id == 3:
                ans = '1'

        return ans

    @property
    def shikikin(self):
        """ 敷金 """
        ans = '0'
        type_id = xint(self.room['deposit_type1']['id'])
        if type_id == 10:
            notation_id = xint(self.room['deposit_notation1']['id'])
            value = xstr(self.room['deposit_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2:
                ans = float_normalize(xfloat(value) / 10000)
            elif notation_id == 3:
                ans = float_normalize(xfloat(value))

        return ans

    @property
    def shikikin_unit_code(self):
        """ 敷金単位区分コード """
        ans = ''
        type_id = xint(self.room['deposit_type1']['id'])
        value = xstr(self.room['deposit_value1'])
        if type_id == 10 and value != '0':
            notation_id = xint(self.room['deposit_notation1']['id'])
            if notation_id == 2:
                ans = '2'
            elif notation_id == 3:
                ans = '1'

        return ans

    @property
    def hosyokin(self):
        """ 保証金 """
        ans = '0'
        type_id = xint(self.room['deposit_type1']['id'])
        if type_id in (20, 30):
            notation_id = xint(self.room['deposit_notation1']['id'])
            value = xstr(self.room['deposit_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2:
                ans = float_normalize(xfloat(value) / 10000)
            elif notation_id == 3:
                ans = float_normalize(xfloat(value))

        return ans

    @property
    def hosyokin_unit_code(self):
        """ 保証金単位区分コード """
        ans = ''
        type_id = xint(self.room['deposit_type1']['id'])
        value = xstr(self.room['deposit_value1'])
        if type_id in (20, 30) and value != '0':
            notation_id = xint(self.room['deposit_notation1']['id'])
            if notation_id == 2:
                ans = '2'
            elif notation_id == 3:
                ans = '1'

        return ans

    @property
    def syokyakukin(self):
        """ 償却金 """
        ans = '0'
        type_id = xint(self.room['key_money_type1']['id'])
        if type_id == 22:
            notation_id = xint(self.room['key_money_notation1']['id'])
            value = xstr(self.room['key_money_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2:
                ans = float_normalize(xfloat(value) / 10000)
            elif notation_id == 3:
                ans = float_normalize(xfloat(value))

        return ans

    @property
    def syokyakukin_unit_code(self):
        """ 償却金単位区分コード """
        ans = ''
        type_id = xint(self.room['key_money_type1']['id'])
        value = xstr(self.room['key_money_value1'])
        if type_id == 22 and value != '0':
            notation_id = xint(self.room['key_money_notation1']['id'])
            if notation_id == 2:
                ans = '2'
            elif notation_id == 3:
                ans = '1'

        return ans

    @property
    def shikibiki(self):
        """ 敷引・解約引き """
        ans = '0'
        type_id = xint(self.room['key_money_type1']['id'])
        if type_id in (20, 21):
            notation_id = xint(self.room['key_money_notation1']['id'])
            value = xstr(self.room['key_money_value1'])
            if notation_id == 1:
                ans = '0'
            elif notation_id == 2:
                ans = float_normalize(xfloat(value) / 10000)
            elif notation_id == 3:
                ans = float_normalize(xfloat(value))

        return ans

    @property
    def shikibiki_unit_code(self):
        """ 敷引単位区分コード """
        ans = ''
        type_id = xint(self.room['key_money_type1']['id'])
        value = xstr(self.room['key_money_value1'])
        if type_id in (20, 21) and value != '0':
            notation_id = xint(self.room['key_money_notation1']['id'])
            if notation_id == 2:
                ans = '2'
            elif notation_id == 3:
                ans = '1'

        return ans

    @property
    def room_status_code(self):
        ans = '2'
        if self.room['room_status']['for_rent']:
            ans = '1'

        return ans

    @property
    def vacancy_status_code(self):
        """ 空室種別コード """
        id = xstr(self.room['vacancy_status']['id'])
        ans = xstr(CodeManager.get_instance().vacancy_statuses.get(id))

        if ans == '3':
            year = xint(self.room['live_start_year'])
            month = xint(self.room['live_start_month'])
            day_id = xint(self.room['live_start_day']['id'])
            if year == 0 or month == 0 or day_id == 0:
                ans = '2'   # 相談

        return ans

    @property
    def live_start_year(self):
        """ 入居可能年 """
        ans = ''
        if self.vacancy_status_code == '3':
            ans = xstr(self.room['live_start_year'])

        return ans

    @property
    def live_start_month(self):
        """ 入居可能月 """
        ans = ''
        if self.vacancy_status_code == '3':
            ans = '{0:0>2}'.format(xstr(self.room['live_start_month']))

        return ans

    @property
    def live_start_day_code(self):
        """ 入居可能日コード"""
        ans = ''
        if self.vacancy_status_code == '3':
            id = xstr(self.room['live_start_day']['id'])
            ans = xstr(CodeManager.get_instance().month_days.get(id))

        return ans

    @property
    def contract_type_code(self):
        """ 契約種別コード　"""
        ans = '0'     # 普通借家
        if self.room['rental_type']['is_limited_rent']:
            ans = '1'     #定期借家

        return ans

    @property
    def contract_span_type_code(self):
        """ 契約期間区分コード """
        ans = ''
        if xint(self.room['contract_years']) > 0 or xint(self.room['contract_months']) > 0:
            ans = '1'   # 期間

        return ans

    @property
    def contract_years(self):
        """ 契約期間年 """
        ans = ''

        data = xint(self.room['contract_years'])
        if data > 0:
            ans = '{0:0>2}'.format(xstr(data))

        return ans

    @property
    def contract_months(self):
        """ 契約期間月 """
        ans = ''

        data = xint(self.room['contract_months'])
        if data > 0:
            ans = '{0:0>2}'.format(xstr(data))

        return ans

    @property
    def insurance_fee(self):
        """ 火災保険金額 """
        ans = ''

        span = xint(self.room['insurance_years'])
        fee = xint(self.room['insurance_fee'])

        if span > 0 and fee > 1000:
            data = fee
            if self.room['insurance_fee_tax_type']['is_excluding']:
                data = int(data * (1 + SystemInfo.get_instance().tax_rate))

            ans = float_normalize(data / 10000)

        return ans

    @property
    def insurance_span(self):
        """ 火災保険期間 """
        ans = ''

        span = xint(self.room['insurance_years'])
        fee = xint(self.room['insurance_fee'])

        if span > 0 and fee > 1000:
            ans = xstr(span)

        return ans

    @property
    def free_rent(self):
        """ フリーレント """
        ans = ''
        id = xint(self.room['free_rent_type']['id'])
        if id == 1:
            ans = xstr(self.room['free_rent_months'])
        elif id == 2:
            year = xint(self.room['free_rent_limit_year'])
            month = xint(self.room['free_rent_limit_month'])
            if year >= datetime.date.today().year:
                if datetime.date.today().month <= month <= 12:
                    if month >= 12:
                        ans = '1'
                    else:
                        ans = xstr(month + 1)

        return ans

    @property
    def free_rent_type_code(self):
        """ フリーレント単位区別コード """
        ans = ''
        if self.free_rent != '':
            id = xint(self.room['free_rent_type']['id'])
            if id == 1:
                ans = '1'
            elif id == 2:
                ans = '2'

        return ans

    @property
    def initial_costs(self):
        """ その他初期費用 """
        ans = ''

        if self.room['document_cost_existence']['is_exist']:
            if ans != '':
                ans += '/'
            ans += '書類代'
            cost = xint(self.room['document_cost'])
            if cost > 0:
                if self.room['document_cost_tax_type']['is_excluding']:
                    cost = int(cost * (1 + SystemInfo.get_instance().tax_rate))
                if cost < 10000:
                    ans += ' ' + comma_format(cost) + '円'
                else:
                    ans += ' ' + float_normalize(cost / 10000) + '万円'

        if self.room['key_change_cost_existence']['is_exist']:
            if ans != '':
                ans += '/'
            ans += '鍵交換代'
            cost = xint(self.room['key_change_cost'])
            if cost > 0:
                if self.room['key_change_cost_tax_type']['is_excluding']:
                    cost = int(cost * (1 + SystemInfo.get_instance().tax_rate))
                if cost < 10000:
                    ans += ' ' + comma_format(cost) + '円'
                else:
                    ans += ' ' + float_normalize(cost / 10000) + '万円'

        for index in range(1, 11):
            cost_name = xstr(self.room['initial_cost_name' + xstr(index)])
            if cost_name != '':
                if ans != '':
                    ans += '/'
                ans += cost_name
                cost = xint(self.room['initial_cost' + xstr(index)])
                if cost > 0:
                    if self.room['initial_cost_tax_type' + xstr(index)]['is_excluding']:
                        cost = int(cost * (1 + SystemInfo.get_instance().tax_rate))
                    if cost < 10000:
                        ans += ' ' + comma_format(cost) + '円'
                    else:
                        ans += ' ' + float_normalize(cost / 10000) + '万円'

        return ans

    @property
    def trader_name(self):
        """ 他社賃貸管理業者名 """
        ans = ''
        if self.transaction_mode_code == '4':
            if self.room['building']['management_type']['is_condo_management']:
                # 分譲管理の部屋の場合
                if xint(self.room['condo_trader']['id']) != 0:
                    ans = xstr(self.room['condo_trader']['trader_name'])
            else:
                # 分譲管理のマンションではない場合
                if xint(self.room['building']['trader']['id']) != 0:
                    ans = xstr(self.room['building']['trader']['trader_name'])

            if ans == '':
                ans = '他社管理'

        return DataHelper.sanitize(ans)

    @property
    def trader_staff_name(self):
        """ 他社賃貸管理担当者名 """
        ans = ''
        if self.transaction_mode_code == '4':
            ans = '担当者'

        return ans

    @property
    def trader_tel(self):
        """ 他社賃貸管理業者電話番号 """
        ans = ''
        if self.transaction_mode_code == '4':
            if self.room['building']['management_type']['is_condo_management']:
                # 分譲管理の部屋の場合
                if xint(self.room['condo_trader']['id']) != 0:
                    ans = xstr(self.room['condo_trader']['tel1'])
            else:
                # 分譲管理のマンションではない場合
                if xint(self.room['building']['trader']['id']) != 0:
                    ans = xstr(self.room['building']['trader']['tel1'])

            if ans == '':
                ans = '999-999-9999'

        return DataHelper.sanitize(ans)

    @property
    def trader_checked_date(self):
        """ 元付確認日 """
        ans = ''
        if self.transaction_mode_code == '4':
            ans = xstr(self.room['updated_date']).replace('-', '')

        return ans

    @property
    def corp_contract_type_code(self):
        """ 法人限定区分コード """
        ans = '9'
        id = xint(self.room['corp_contract_type']['id'])
        if id == 5:
            ans = '1'
        elif id == 4:
            ans = '2'

        return ans

    @property
    def student_type_code(self):
        """ 学生限定区分コード """
        ans = '9'
        id = xint(self.room['student_type']['id'])
        if id == 5:
            ans = '1'
        elif id == 4:
            ans = '2'

        return ans

    @property
    def gender_type_code(self):
        """ 性別限定区分コード """
        ans = '9'
        id = xint(self.room['only_woman_type']['id'])
        if xint(self.room['only_woman_type']['id']) == 4:
            ans = '2'
        elif xint(self.room['only_man_type']['id']) == 4:
            ans = '1'

        return ans

    @property
    def live_together_type_code(self):
        """ 二人限定区分コード """
        ans = '9'
        id = xint(self.room['live_together_type']['id'])
        if id == 1:
            ans = '1'

        return ans

    @property
    def children_type_code(self):
        """ 子供入居区分コード """
        ans = '9'
        id = xint(self.room['children_type']['id'])
        if id == 1:
            ans = '1'
        elif id == 2:
            ans = '2'

        return ans

    @property
    def pet_type_code(self):
        """ ペット区分コード """
        ans = '9'
        if self.room['pet_type']['is_ok']:
            ans = '3'

        return ans

    @property
    def instrument_type_code(self):
        """ 楽器区分コード """
        ans = '9'
        id = xint(self.room['instrument_type']['id'])
        if id in (1, 3):
            ans = '3'

        return ans

    @property
    def office_use_type_code(self):
        """ 事務所利用区分コード """
        ans = '9'
        id = xint(self.room['share_type']['id'])
        if id == 2:
            ans = '2'
        elif id == 3:
            ans = '3'

        return ans

    @property
    def room_share_type_code(self):
        """ ルームシェア区分コード """
        ans = '9'
        id = xint(self.room['share_type']['id'])
        if id == 2:
            ans = '2'
        elif id == 3:
            ans = '3'

        return ans

    @property
    def room_area(self):
        """ 専有面積 """
        data = math.floor(xfloat(self.room['room_area']) * 100) / 100
        ans = float_normalize(data)
        return ans

    @property
    def balcony_area(self):
        """ バルコニー面積 """
        data = math.floor(xfloat(self.room['balcony_area']) * 100) / 100
        ans = float_normalize(data)
        return ans

    @property
    def direction_code(self):
        """ 開口向き区分コード """
        id = xstr(self.room['direction']['id'])
        return xstr(CodeManager.get_instance().directions.get(id))

    @property
    def equipment_codes(self):
        """ 設備 """
        ans = ''
        for item in self.room['equipments']:
            if len(ans) >= 299:
                break
            id = xstr(item['equipment']['id'])
            code = xstr(CodeManager.get_instance().equipments.get(id))
            if code:
                if ans != '':
                    ans += '/'
                ans += code

        return ans

    @property
    def is_reformed(self):
        """ リフォーム情報がある場合はTrue """
        ans = False

        year = xint(self.room['reform_year'])
        month = xint(self.room['reform_month'])
        comment = xstr(self.room['reform_comment'])

        if year >= 1000 and 1 <= month <= 12 and comment:
            ans = True

        return ans

    @property
    def reform_year_month(self):
        """ リフォーム年月 """
        ans = ''

        if self.is_reformed:
            ans = '{0}年{1:0>2}月'.format(
                xstr(self.room['reform_year']),
                xstr(self.room['reform_month']),
            )

        return ans

    @property
    def reform_comment(self):
        """ リフォーム内容コメント """
        ans = ''

        if self.is_reformed:
            ans = DataHelper.sanitize(xstr(self.room['reform_comment']))

        return ans

    @property
    def room_note(self):
        """ 部屋備考 """
        ans = xstr(self.room['web_note'])
        return DataHelper.sanitize(ans)

    @property
    def room_catch_copy(self):
        """ 部屋キャッチコピー """
        ans = xstr(self.room['web_catch_copy'])
        return DataHelper.sanitize(ans)

    @property
    def room_appeal(self):
        """ 部屋アピール """
        ans = xstr(self.room['web_appeal'])
        return DataHelper.sanitize(ans)
