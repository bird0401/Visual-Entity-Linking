# MySQLdbのインポート
import MySQLdb
 
# データベースへの接続とカーソルの生成
connection = MySQLdb.connect(
    host='localhost',
    user='scraper',
    passwd='vnajr3495',
    db='scraping')
cursor = connection.cursor()
 
# ここに実行したいコードを入力します
# テーブルの初期化
cursor.execute("DROP TABLE IF EXISTS name_age_list")
 
# テーブルの作成
cursor.execute("""CREATE TABLE name_age_list(
    id INT(11) AUTO_INCREMENT NOT NULL, 
    name VARCHAR(30) NOT NULL COLLATE utf8mb4_unicode_ci, 
    age INT(3) NOT NULL,
    PRIMARY KEY (id)
    )""")
 
# データの追加
cursor.execute("""INSERT INTO name_age_list (name, age)
    VALUES ('タロー', '25'),
    ('ジロー', '23'),
    ('サブロー', '21')
    """)
 
# 一覧の表示
cursor.execute("SELECT * FROM name_age_list")
 
for row in cursor:
    print(row)
 
# 保存を実行
connection.commit()
 
# 接続を閉じる
connection.close()