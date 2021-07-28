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

* Windowsにインストールする場合の手順
1) Python3.8をインストールする。
2) 適切なフォルダにファイル一式を展開する。
3) config.iniファイルを適切に変更する。
4) コマンドプロンプトを開き、展開したフォルダにcdコマンドで移動する。
5) 「python -m venv venv」 とコマンドを入力し、展開したフォルダにvenv仮想環境を作成する。
6) dirコマンドを実行しvenvフォルダができていることを確認する。
7) 「venv\Scripts\activate.bat」とコマンドを入力してvenv仮想環境に切り替える。
8) 「pip3 install pyproj==3.1.0」とコマンドを入力してpyprojをインストールする。
9) 「pip3 install python-dateutil==2.8.1」とコマンドを入力してpython-dateutilをインストールする。
10) 「python main.py」と入力してコンバータの動作を確認する。
11) 「deactivate」と入力してvenv仮想環境を終了する。
12) コマンドプロンプトを閉じる。

* Windowsへのインストール後の起動方法
1) コマンドプロンプトを開き、展開したフォルダにcdコマンドで移動する。
2) 「venv\Scripts\activate.bat」とコマンドを入力してvenv仮想環境に切り替える。
3) 「python main.py」と入力してコンバータを起動する。
4) 「deactivate」と入力してvenv仮想環境を終了する。
5) コマンドプロンプトを閉じる

* Windowsのバッチファイル例
cd [展開したフォルダ]
call venv\Scripts\activate.bat & python main.py


