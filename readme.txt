1.Vasywoksについて
Vasyworks（ベイジーワークス）は賃貸管理業において、空室情報を登録、公開するための一連のシステムの総称です。主に賃貸管理業者（法人および個人）が管理物件の空室情報を賃貸仲介業者に公開するための利用を想定しています。

VasyworksはVasyworksDB（データベース構築プロジェクト）、VasyworksMGR（空室情報データ管理プロジェクト）、VasyworksLIST（空室情報一覧プロジェクト）、VasyworksAPI（空室情報APIプロジェクト）など複数のプロジェクトから構成されています。

2.Vasyworks SUUMOコンバータについて
Vasyworks SUUMOコンバータはVasyworksAPIのデータ連携用APIを用いて、不動産ポータルサイトのSUUMOに一括入稿するためのデータを生成するためのコンバータです。
・vcnv_suumo_1_3はCSVバージョン1.36に対応しています。

3.Vasyworks SUUMOコンバータのライセンスについて
Vasywork SUUMOコンバータのソースコードは山本 泰弘の著作物として、GLPv3のライセンス条件の下で利用できます。GPLv3の条件での利用ができない場合は、商用ライセンス版が必要となります。商用ライセンス版を利用する場合は、1賃貸管理業者（法人および個人）につき1ライセンスが必要となります。

4.動作環境について
Python3の使えるWindowシステムOS環境でご利用ください。（Windowns10とMacOS11は動作確認済み）
開発環境は下記の通りです。
・Python 3.8
・pyproj 3.1.0
・python-dateutil 2.8.1

5. インストールと実行について
1) Python3.8をインストールし、pipコマンドでpyprojとpython-dateutilをインストールしてください。
2) vcnv_suumo_1_3のソースコード一式を適切なディレクトリ（フォルダ）に配置し、config.iniの設定を適切に変更してください。
3) main.pyを実行してください。



