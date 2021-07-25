"""
System Name: Vasyworks
Project Name: vcnv_suumo
Encoding: UTF-8
Copyright (C) 2021 Yasuhiro Yamamoto
"""
import os
import datetime
from lib.convert import *
from common import Api, AppObject, SystemInfo
from .data_helper import DataHelper
from .room_data import RoomData


class Converter(AppObject):
    """
    コンバータ
    """
    progress = None
    progressbar = None

    def __init__(self):
        """ コンストラクタ """
        super().__init__()

        return

    def __del__(self):
        """ デストラクタ """
        super().__del__()

        self.progress = None
        self.progressbar = None

        return

    """
    コンバート処理
    """
    def convert(self):
        """コンバートの実行"""
        self.write_progress('前回送信データのクリア')
        try:
            self.reset_progressbar(6)
            # 送信CSVデータ
            DataHelper.remove_file(os.path.join(SystemInfo.get_instance().output_dir, 'fn_upload.txt'))
            self.update_progressbar(1)
            # 送信制御データ
            DataHelper.remove_file(os.path.join(SystemInfo.get_instance().output_dir, 'fn_upload.trg'))
            self.update_progressbar(2)
            # 送信画像データ
            DataHelper.remove_file(os.path.join(SystemInfo.get_instance().output_dir, 'fn_upload.zip'))
            self.update_progressbar(3)
            # 送信パノラマデータ
            DataHelper.remove_file(os.path.join(SystemInfo.get_instance().output_dir, 'fn_panorama_upload.zip'))
            self.update_progressbar(4)
            # 画像収集用ディレクトリ
            DataHelper.remake_dir(SystemInfo.get_instance().image_dir)
            self.update_progressbar(5)
            # パノラマ収集用ディレクトリ
            DataHelper.remake_dir(SystemInfo.get_instance().panorama_dir)
            self.update_progressbar(6)
            self.write_progress('前回送信データのクリア済')
        except Exception as e:
            self.write_progress('エラーが発生しました。')
            raise

        self.write_progress('データ取得中')
        self.reset_progressbar(1)

        rooms = Api.get_json_data(SystemInfo.get_instance().api_url)
        if not rooms:
            self.write_progress('データ取得失敗')
            raise Exception('データの取得に失敗しました。')

        self.write_progress('データ取得済')

        try:
            room_count = xint(rooms['count'])
            self.write_progress('データ加工中： {0}件'.format(room_count))
            self.reset_progressbar(room_count)
            self.output_csv_data(rooms['list'], room_count)
            self.write_progress('データ加工済： {0}件'.format(room_count))

            self.write_progress('画像圧縮中')
            self.reset_progressbar(2)
            self.compress_images()
            self.update_progressbar(1)
            self.compress_panoramas()
            self.update_progressbar(2)
            self.write_progress('画像圧縮済')

            self.write_progress('送信制御ファイル出力中')
            self.reset_progressbar(1)
            self.output_sent_file()
            self.update_progressbar(1)
            self.write_progress('コンバート完了： {0}件'.format(room_count))

            del rooms
            return

        except Exception as e:
            self.write_progress('エラーが発生しました。')
            del rooms
            raise

    def output_csv_data(self, rooms, room_count):
        """ CSVデータ出力 """
        csv_file = None
        room_data = None

        try:
            file_path = os.path.join(SystemInfo.get_instance().output_dir, 'fn_upload.txt')
            csv_file = open(file=file_path, mode='w', encoding='shift_jis',)

            # ヘッダー部
            header = '1'  # レコードタイプ
            header += '\t{0}'.format(SystemInfo.get_instance().company_code)  # 会社コード
            header += '\t{0}'.format(SystemInfo.get_instance().branch_code)  # 支店コード
            header += '\t{0}'.format(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))  # ファイル作成日時

            header += '\n'
            csv_file.write(header)

            # データ部
            if room_count > 0:
                count = 0
                for room in rooms:
                    room_data = RoomData(room)

                    # 送信画像・パノラマ収集
                    room_data.image_set.collect()
                    room_data.panorama_set.collect()

                    # テキストデータ生成
                    data = '4'  # レコードタイプ
                    data += '\t{0}'.format(SystemInfo.get_instance().company_code)  # 会社コード
                    data += '\t{0}'.format(SystemInfo.get_instance().branch_code)  # 支店コード
                    data += '\t{0}'.format(room_data.room_id)  # 一括入稿用物件コード
                    data += '\t{0}'.format('1')  # 物件区分コード
                    data += '\t{0}'.format(room_data.building_name)  # 物件名
                    data += '\t{0}'.format('1')  # 物件名公開フラグ
                    data += '\t{0}'.format(room_data.building_floors)  # 階建
                    data += '\t{0}'.format(room_data.room_floor)  # 階数
                    data += '\t{0}'.format(room_data.room_no)  # 部屋番号
                    data += '\t{0}'.format('1')  # 部屋番号公開フラグ
                    data += '\t{0}'.format(room_data.building_type_code)  # 物件種別コード
                    data += '\t{0}'.format(room_data.structure_code)  # 構造種別コード
                    data += '\t{0}'.format(room_data.build_year)  # 築年
                    data += '\t{0}'.format(room_data.build_month)  # 築月
                    data += '\t{0}'.format('')  # 新築区分コード
                    data += '\t{0}'.format(room_data.room_count)  # 部屋数
                    data += '\t{0}'.format(room_data.layout_type_code)  # 間取タイプ区分コード
                    data += '\t{0}'.format(room_data.rent)  # 賃料額
                    data += '\t{0}'.format(room_data.condo_fees)  # 管理費額
                    data += '\t{0}'.format(room_data.get_railway_code(1))  # 沿線コード（交通1）
                    data += '\t{0}'.format(room_data.get_station_code(1))  # 駅コード（交通1）
                    data += '\t{0}'.format('')  # REINSコード（交通1） 　[(REINS)発行沿線・駅コード]
                    data += '\t{0}'.format(room_data.get_arrival_type_code(1))  # 交通手段コード
                    data += '\t{0}'.format(room_data.get_station_time(1))  # 所要時間（交通1） （徒歩・バス利用・車利用）
                    data += '\t{0}'.format(room_data.get_bus_stop(1))  # バス停名（交通1）
                    data += '\t{0}'.format(room_data.get_bus_stop_time(1))  # バス停歩時間（交通1）
                    data += '\t{0}'.format('')  # 車距離（交通1）
                    data += '\t{0}'.format(room_data.address)  # 住所名
                    data += '\t{0}'.format(room_data.house_no)  # 番地
                    data += '\t{0}'.format(room_data.building_no)  # 街区号棟
                    data += '\t{0}'.format('0')  # 詳細住所公開フラグ
                    data += '\t{0}'.format('')  # 貸主名
                    data += '\t{0}'.format(room_data.vacancy_status_code)  # 入居区分コード
                    data += '\t{0}'.format(room_data.live_start_year)  # 入居年
                    data += '\t{0}'.format(room_data.live_start_month)  # 入居月
                    data += '\t{0}'.format(room_data.live_start_day_code)  # 入居旬区分コード
                    data += '\t{0}'.format(room_data.transaction_mode_code)  # 取引態様区分コード
                    data += '\t{0}'.format('0')  # 星マークフラグ （客付可を示すマーク）
                    data += '\t{0}'.format('')  # 貸主負担割合
                    data += '\t{0}'.format('')  # 借主負担割合
                    data += '\t{0}'.format('')  # 元付配分
                    data += '\t{0}'.format('')  # 客付配分
                    data += '\t{0}'.format(room_data.trader_name)  # 元付業者名
                    data += '\t{0}'.format(room_data.trader_staff_name)  # 元付業者担当者名
                    data += '\t{0}'.format(room_data.trader_tel)  # 元付業者電話番号
                    data += '\t{0}'.format(room_data.trader_checked_date)  # 元付確認日
                    data += '\t{0}'.format(room_data.building_code)  # 貴社物件コード
                    data += '\t{0}'.format('')  # 貴社管理コード1
                    data += '\t{0}'.format('')  # 貴社管理コード2
                    data += '\t{0}'.format(room_data.reikin)  # 礼金額
                    data += '\t{0}'.format(room_data.reikin_unit_code)  # 礼金単位区分コード
                    data += '\t{0}'.format(room_data.shikikin)  # 敷金額
                    data += '\t{0}'.format(room_data.shikikin_unit_code)  # 敷金単位区分コード
                    data += '\t{0}'.format('')  # 敷金積み増し条件区分コード
                    data += '\t{0}'.format('')  # 敷金積み増し額
                    data += '\t{0}'.format('')  # 敷金積み増し単位区分コード
                    data += '\t{0}'.format(room_data.syokyakukin)  # 償却金
                    data += '\t{0}'.format(room_data.hosyokin_unit_code)  # 償却金単位区分コード
                    data += '\t{0}'.format(room_data.hosyokin)  # 保証金
                    data += '\t{0}'.format(room_data.hosyokin_unit_code)  # 保証金単位区分コード
                    data += '\t{0}'.format(room_data.shikibiki)  # 敷引
                    data += '\t{0}'.format(room_data.shikibiki_unit_code)  # 敷引単位区分コード
                    data += '\t{0}'.format('1')  # 損保フラグ
                    data += '\t{0}'.format(room_data.insurance_fee)  # 損保金額
                    data += '\t{0}'.format(room_data.insurance_span)  # 損保金額契約年数
                    data += '\t{0}'.format(room_data.contract_type_code)  # 契約期間区分コード
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format(room_data.garage_type_code)  # 駐車場状況区分コード
                    data += '\t{0}'.format(room_data.garage_fee)  # 駐車料金
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format(room_data.garage_distance)  # 近隣駐車場距離
                    data += '\t{0}'.format('')  # 駐車場備考区分コード
                    data += '\t{0}'.format('')  # バス路線名2
                    data += '\t{0}'.format('')  # バス停名2
                    data += '\t{0}'.format('')  # バス路線名3
                    data += '\t{0}'.format('')  # バス停名3
                    data += '\t{0}'.format(room_data.corp_contract_type_code)  # 法人限定区分コード
                    data += '\t{0}'.format(room_data.student_type_code)  # 学生限定区分コード
                    data += '\t{0}'.format(room_data.gender_type_code)  # 性別限定区分コード
                    data += '\t{0}'.format('9')  # 単身者限定区分コード
                    data += '\t{0}'.format(room_data.live_together_type_code)  # 二人限定区分コード
                    data += '\t{0}'.format(room_data.children_type_code)  # 子供入居区分コード
                    data += '\t{0}'.format(room_data.pet_type_code)  # ペット区分コード
                    data += '\t{0}'.format(room_data.instrument_type_code)  # 楽器区分コード
                    data += '\t{0}'.format(room_data.free_rent)  # フリーレント
                    data += '\t{0}'.format(room_data.free_rent_type_code)  # フリーレント単位区分コード
                    data += '\t{0}'.format(room_data.room_area)  # 面積
                    data += '\t{0}'.format(room_data.direction_code)  # 開口向き区分コード
                    data += '\t{0}'.format(room_data.get_japanese_style_room(1))  # 和室間取詳細1
                    data += '\t{0}'.format(room_data.get_japanese_style_room(2))  # 和室間取詳細2
                    data += '\t{0}'.format(room_data.get_japanese_style_room(3))  # 和室間取詳細3
                    data += '\t{0}'.format(room_data.get_japanese_style_room(4))  # 和室間取詳細4
                    data += '\t{0}'.format(room_data.get_japanese_style_room(5))  # 和室間取詳細5
                    data += '\t{0}'.format(room_data.get_japanese_style_room(6))  # 和室間取詳細6
                    data += '\t{0}'.format(room_data.get_japanese_style_room(7))  # 和室間取詳細7
                    data += '\t{0}'.format(room_data.get_japanese_style_room(8))  # 和室間取詳細8
                    data += '\t{0}'.format(room_data.get_japanese_style_room(9))  # 和室間取詳細9
                    data += '\t{0}'.format(room_data.get_japanese_style_room(10))  # 和室間取詳細10
                    data += '\t{0}'.format(room_data.get_western_style_room(1))  # 洋室間取詳細1
                    data += '\t{0}'.format(room_data.get_western_style_room(2))  # 洋室間取詳細2
                    data += '\t{0}'.format(room_data.get_western_style_room(3))  # 洋室間取詳細3
                    data += '\t{0}'.format(room_data.get_western_style_room(4))  # 洋室間取詳細4
                    data += '\t{0}'.format(room_data.get_western_style_room(5))  # 洋室間取詳細5
                    data += '\t{0}'.format(room_data.get_western_style_room(6))  # 洋室間取詳細6
                    data += '\t{0}'.format(room_data.get_western_style_room(7))  # 洋室間取詳細7
                    data += '\t{0}'.format(room_data.get_western_style_room(8))  # 洋室間取詳細8
                    data += '\t{0}'.format(room_data.get_western_style_room(9))  # 洋室間取詳細9
                    data += '\t{0}'.format(room_data.get_western_style_room(10))  # 洋室間取詳細10
                    data += '\t{0}'.format(room_data.kitchen)  # LDK間取詳細
                    data += '\t{0}'.format(room_data.get_store_room(1))  # 納戸間取詳細1
                    data += '\t{0}'.format(room_data.get_store_room(2))  # 納戸間取詳細2
                    data += '\t{0}'.format(room_data.get_store_room(3))  # 納戸間取詳細3
                    data += '\t{0}'.format(room_data.get_loft(1))  # ロフト間取詳細1
                    data += '\t{0}'.format(room_data.get_loft(2))  # ロフト間取詳細2
                    data += '\t{0}'.format('')  # 書斎間取詳細1
                    data += '\t{0}'.format('')  # 書斎間取詳細2
                    data += '\t{0}'.format(room_data.get_sun_room(1))  # サンルーム間取詳細1
                    data += '\t{0}'.format(room_data.get_sun_room(2))  # サンルーム間取詳細2
                    data += '\t{0}'.format('')  # グルニエ間取詳細1
                    data += '\t{0}'.format('')  # グルニエ間取詳細2
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # その他沿線駅名
                    data += '\t{0}'.format('')  # その他沿線駅交通区分コード
                    data += '\t{0}'.format('')  # その他沿線駅所要時間
                    data += '\t{0}'.format('')  # その他バス停名
                    data += '\t{0}'.format('')  # その他バス停徒歩分
                    data += '\t{0}'.format('')  # その他車距離
                    data += '\t{0}'.format('')  # 設備環境名1
                    data += '\t{0}'.format('')  # 設備環境距離1
                    data += '\t{0}'.format('')  # 隣接設備環境名1
                    data += '\t{0}'.format('')  # 設備環境単位区分コード1
                    data += '\t{0}'.format('')  # １階入居店舗コメント
                    data += '\t{0}'.format('9')  # 管理形態区分コード
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format(room_data.room_note)  # その他備考
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('1')  # 物件名特記表示フラグ
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # メインキャッチ1
                    data += '\t{0}'.format('')  # メインキャッチ2
                    data += '\t{0}'.format('')  # サブキャッチ1
                    data += '\t{0}'.format('')  # サブキャッチ2
                    data += '\t{0}'.format('')  # サブキャッチ3
                    data += '\t{0}'.format('')  # サブキャッチ4
                    data += '\t{0}'.format('')  # サブキャッチ5
                    data += '\t{0}'.format('')  # サブキャッチ6
                    data += '\t{0}'.format('')  # サブキャッチ7
                    data += '\t{0}'.format('')  # サブキャッチ8
                    data += '\t{0}'.format('')  # サブキャッチ9
                    data += '\t{0}'.format('')  # サブキャッチ10
                    data += '\t{0}'.format('')  # フリーコメント
                    data += '\t{0}'.format('0')  # 削除指示フラグ
                    data += '\t{0}'.format(room_data.room_status_code)  # 空室状況区分コード
                    data += '\t{0}'.format('1')  # 掲載指示フラグ1 （SUUMOネット掲載指示）
                    data += '\t{0}'.format('0')  # 掲載指示フラグ2 (会社間流通サイト掲載指示）
                    data += '\t{0}'.format('')  # 掲載指示フラグ3
                    data += '\t{0}'.format('')  # 掲載指示フラグ4
                    data += '\t{0}'.format('')  # 掲載指示フラグ5
                    data += '\t{0}'.format('')  # 掲載指示フラグ6
                    data += '\t{0}'.format('')  # 掲載指示フラグ7
                    data += '\t{0}'.format('')  # 掲載指示フラグ8
                    data += '\t{0}'.format('')  # 掲載指示フラグ9
                    data += '\t{0}'.format('')  # 掲載指示フラグ10
                    data += '\t{0}'.format('')  # ほか初期費用（入会金等）
                    data += '\t{0}'.format(room_data.initial_costs)  # ほか初期費用詳細
                    data += '\t{0}'.format('')  # 仲介手数料
                    data += '\t{0}'.format('')  # 仲介手数料区分コード
                    data += '\t{0}'.format('')  # バス路線名
                    data += '\t{0}'.format('')  # バス停名
                    data += '\t{0}'.format('')  # 保証会社加入形態区分コード
                    data += '\t{0}'.format('')  # 保証会社区分コード
                    data += '\t{0}'.format('')  # 保証料
                    data += '\t{0}'.format(room_data.room_catch_copy)  # ネット用キャッチ
                    data += '\t{0}'.format(room_data.room_appeal)  # ネット用キャッチコメント
                    data += '\t{0}'.format(room_data.get_railway_code(2))  # 沿線コード（交通2）
                    data += '\t{0}'.format(room_data.get_station_code(2))  # 駅コード（交通2）
                    data += '\t{0}'.format('')  # REINSコード（交通2） 　[(財)不動産流通近代化センター(REINS)発行沿線・駅コード]
                    data += '\t{0}'.format(room_data.get_arrival_type_code(2))  # 交通手段コード2
                    data += '\t{0}'.format(room_data.get_station_time(2))  # 所要時間（交通2） （徒歩・バス利用・車利用）
                    data += '\t{0}'.format(room_data.get_bus_stop(2))  # バス停名（交通2）
                    data += '\t{0}'.format(room_data.get_bus_stop_time(2))  # バス停歩時間（交通2）
                    data += '\t{0}'.format('')  # 車距離（交通2）
                    data += '\t{0}'.format(room_data.get_railway_code(3))  # 沿線コード（交通3）
                    data += '\t{0}'.format(room_data.get_station_code(3))  # 駅コード（交通3）
                    data += '\t{0}'.format('')  # REINSコード（交通3） 　[(財)不動産流通近代化センター(REINS)発行沿線・駅コード]
                    data += '\t{0}'.format(room_data.get_arrival_type_code(3))  # 交通手段コード3
                    data += '\t{0}'.format(room_data.get_station_time(3))  # 所要時間（交通3） （徒歩・バス利用・車利用）
                    data += '\t{0}'.format(room_data.get_bus_stop(3))  # バス停名（交通3）
                    data += '\t{0}'.format(room_data.get_bus_stop_time(3))  # バス停歩時間（交通3）
                    data += '\t{0}'.format('')  # 車距離（交通3）
                    data += '\t{0}'.format('')  # 設備環境名2
                    data += '\t{0}'.format('')  # 設備環境距離2
                    data += '\t{0}'.format(room_data.show_on_map)  # 地図表示フラグ
                    data += '\t{0}'.format(room_data.lat)  # 緯度
                    data += '\t{0}'.format(room_data.lng)  # 経度
                    data += '\t{0}'.format(room_data.get_facility_category(1))  # 周辺環境1 目的地カテゴリ
                    data += '\t{0}'.format(room_data.get_facility_name(1))  # 周辺環境1 目的地名
                    data += '\t{0}'.format(room_data.get_facility_distance(1))  # 周辺環境1 目的地距離
                    data += '\t{0}'.format(room_data.get_facility_category(2))  # 周辺環境2 目的地カテゴリ
                    data += '\t{0}'.format(room_data.get_facility_name(2))  # 周辺環境2 目的地名
                    data += '\t{0}'.format(room_data.get_facility_distance(2))  # 周辺環境2 目的地距離
                    data += '\t{0}'.format(room_data.get_facility_category(3))  # 周辺環境3 目的地カテゴリ
                    data += '\t{0}'.format(room_data.get_facility_name(3))  # 周辺環境3 目的地名
                    data += '\t{0}'.format(room_data.get_facility_distance(3))  # 周辺環境3 目的地距離
                    data += '\t{0}'.format(room_data.get_facility_category(4))  # 周辺環境4 目的地カテゴリ
                    data += '\t{0}'.format(room_data.get_facility_name(4))  # 周辺環境4 目的地名
                    data += '\t{0}'.format(room_data.get_facility_distance(4))  # 周辺環境4 目的地距離
                    data += '\t{0}'.format(room_data.get_facility_category(5))  # 周辺環境5 目的地カテゴリ
                    data += '\t{0}'.format(room_data.get_facility_name(5))  # 周辺環境5 目的地名
                    data += '\t{0}'.format(room_data.get_facility_distance(5))  # 周辺環境5 目的地距離
                    data += '\t{0}'.format(room_data.get_facility_category(6))  # 周辺環境6 目的地カテゴリ
                    data += '\t{0}'.format(room_data.get_facility_name(6))  # 周辺環境6 目的地名
                    data += '\t{0}'.format(room_data.get_facility_distance(6))  # 周辺環境6 目的地距離
                    data += '\t{0}'.format(room_data.building_rooms)  # 総戸数
                    data += '\t{0}'.format(room_data.building_undergrounds)  # 階建（地下）
                    data += '\t{0}'.format(room_data.balcony_area)  # バルコニー面積
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format(room_data.image_set.get_main_building_comment())  # 外観写真コメント
                    data += '\t{0}'.format(room_data.image_set.get_perspective_comment())  # 外観パースコメント
                    data += '\t{0}'.format(room_data.image_set.get_main_room_category_code())  # 内観写真カテゴリ区分コード
                    data += '\t{0}'.format(room_data.image_set.get_main_room_comment())  # 内観写真コメント
                    data += '\t{0}'.format(room_data.image_set.get_base_category_code(1))  # ネット基本画像カテゴリ区分コード1
                    data += '\t{0}'.format(room_data.image_set.get_base_comment(1))  # ネット基本画像コメント1
                    data += '\t{0}'.format(room_data.image_set.get_base_category_code(2))  # ネット基本画像カテゴリ区分コード2
                    data += '\t{0}'.format(room_data.image_set.get_base_comment(2))  # ネット基本画像コメント2
                    data += '\t{0}'.format(room_data.image_set.get_base_category_code(3))  # ネット基本画像カテゴリ区分コード3
                    data += '\t{0}'.format(room_data.image_set.get_base_comment(3))  # ネット基本画像コメント3
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(1))  # 追加画像カテゴリ区分コード1
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(1))  # 追加画像コメント1
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(2))  # 追加画像カテゴリ区分コード2
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(2))  # 追加画像コメント2
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(3))  # 追加画像カテゴリ区分コード3
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(3))  # 追加画像コメント3
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(4))  # 追加画像カテゴリ区分コード4
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(4))  # 追加画像コメント4
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(5))  # 追加画像カテゴリ区分コード5
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(5))  # 追加画像コメント5
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(6))  # 追加画像カテゴリ区分コード6
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(6))  # 追加画像コメント6
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(7))  # 追加画像カテゴリ区分コード7
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(7))  # 追加画像コメント7
                    data += '\t{0}'.format(room_data.image_set.get_addition_category_code(8))  # 追加画像カテゴリ区分コード8
                    data += '\t{0}'.format(room_data.image_set.get_addition_comment(8))  # 追加画像コメント8
                    data += '\t{0}'.format('')  # R図面雛形区分コード
                    data += '\t{0}'.format('')  # その他諸費用
                    data += '\t{0}'.format('')  # SUUMO内優先画像区分コード
                    data += '\t{0}'.format('')  # 隣接設備環境名2
                    data += '\t{0}'.format('')  # 設備環境単位区分コード2
                    data += '\t{0}'.format(room_data.equipment_codes)  # 特徴項目
                    data += '\t{0}'.format(room_data.office_use_type_code)  # 事務所利用区分コード
                    data += '\t{0}'.format(room_data.reform_comment)  # リフォーム箇所
                    data += '\t{0}'.format(room_data.reform_year_month)  # リフォーム時期
                    data += '\t{0}'.format('')  # リフォーム補足
                    data += '\t{0}'.format(room_data.contract_span_type_code)  # 契約期間単位区分コード
                    data += '\t{0}'.format(room_data.contract_years)  # 契約期間年
                    data += '\t{0}'.format(room_data.contract_months)  # 契約期間月
                    data += '\t{0}'.format('')  # 特優賃（入居負担額下限）
                    data += '\t{0}'.format('')  # 特優賃（入居負担額上限）
                    data += '\t{0}'.format('')  # 特優賃変動区分コード
                    data += '\t{0}'.format('')  # 特優賃（上昇率）
                    data += '\t{0}'.format('')  # 特優賃（家賃補助年数）
                    data += '\t{0}'.format('')  # 特優賃（補足）
                    data += '\t{0}'.format('')  # フリーレント(条件詳細)
                    data += '\t{0}'.format(room_data.room_share_type_code)  # ルームシェア区分コード
                    data += '\t{0}'.format('')  # おすすめピックアップピクト指定1
                    data += '\t{0}'.format('')  # おすすめピックアップピクト指定2
                    data += '\t{0}'.format('')  # おすすめピックアップピクト指定3
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('0')  # 広告料応相談
                    data += '\t{0}'.format('0')  # 自社媒体掲載対象フラグ
                    data += '\t{0}'.format('2')  # 他社HP掲載対象区分コード
                    data += '\t{0}'.format('2')  # 会社間物件検索コピー許可設定区分コード
                    data += '\t{0}'.format('0')  # 見学予約フラグ
                    data += '\t{0}'.format(room_data.panorama_set.is_exist)  # パノラマ掲載指示
                    data += '\t{0}'.format('')  # パノラマID
                    data += '\t{0}'.format('1')  # 部屋番号表示フラグ
                    data += '\t{0}'.format('0')  # スマピク掲載指示
                    data += '\t{0}'.format('')  # 住所コード
                    data += '\t{0}'.format('0')  # 間取り画像削除指示
                    data += '\t{0}'.format('0')  # 外観画像削除指示
                    data += '\t{0}'.format('0')  # 外観パース画像削除指示
                    data += '\t{0}'.format('0')  # 地図画像削除指示（会社間用）
                    data += '\t{0}'.format('0')  # 周辺写真画像削除指示（会社間用）
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー
                    data += '\t{0}'.format('')  # フィラー

                    data += '\n'
                    csv_file.write(data)

                    del room_data

                    # 進捗表示
                    count += 1
                    self.update_progressbar(count)

            csv_file.close()

            return

        except:
            if csv_file:
                csv_file.close()

            if room_data:
                del room_data

            raise Exception('CSVデータ出力に失敗しました。')

    def compress_images(self):
        """画像データを圧縮して送信用画像データを作成"""
        file_path = os.path.join(SystemInfo.get_instance().output_dir, 'fn_upload.zip')
        data_dir = SystemInfo.get_instance().image_dir
        DataHelper.make_image_zip(file_path, data_dir)

    def compress_panoramas(self):
        """パノラマデータを圧縮して送信用画像データを作成"""
        file_path = os.path.join(SystemInfo.get_instance().output_dir, 'fn_panorama_upload.zip')
        data_dir = SystemInfo.get_instance().panorama_dir
        DataHelper.make_image_zip(file_path, data_dir)

    @classmethod
    def output_sent_file(cls):
        """ 物件送信制御ファイルの出力 """
        sent_file = None

        try:
            file_path = os.path.join(SystemInfo.get_instance().output_dir, 'fn_upload.trg')
            sent_file = open(file=file_path, mode='w', encoding='shift_jis',)
            sent_file.close()   # 何も出力しない。

            return

        except:
            if sent_file:
                sent_file.close()
            raise Exception('物件送信制御ファイルの出力に失敗しました。')


    """
    進捗表示用メソッド
    """
    def write_progress(self, message):
        """ 進捗状況の書き込み """
        if self.progress:
            self.progress['text'] = '【{0}】'.format(message)
            self.progress.update()
        return

    def reset_progressbar(self, maximum):
        """ プログレスバーのリセット """
        if self.progressbar:
            self.progressbar['maximum'] = maximum
            self.progressbar.configure(value=0)
            self.progressbar.update()
        return

    def update_progressbar(self, count):
        """ プログレスバーの更新 """
        if self.progressbar:
            self.progressbar.configure(value=count)
            self.progressbar.update()
        return
