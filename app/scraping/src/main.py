from extract_wikidata_ids_by_category import extract_wikidata_ids_by_category
from extract_wikidata_relations_by_category import extract_wikidata_relations_by_category
from filter_existing_wikimedia_and_wikipedia import filter_existing_wikimedia, filter_existing_wikipedia
from create_id_to_name import create_id_to_name
from relations_to_text import relations_to_text_by_category
from clean_relations_text import clean_relations_text_by_category
from extract_images import extract_images
from extract_article_by_category import extract_article_by_category
from create_ids_file import create_ids_file

# 作成されるファイル
# - ids_labels.json
# - wikidata.json
# - wikidata_with_commons.json
# images/{id}/{image_file_name}.jpg
# wikipedia/{id}.txt

import sys
# TODO: imagesディレクトリには、airticle filtering前のエンティティも含まれるため、今後画像枚数の検証などを行う際にはこれらは分けて行う必要がある
# TODO: 一番初めに収集したwikidataのエンティティから、どのくらい削られて最終的なデータセットが作られたのかを表にする
# TODO: clean時のディレクトリ名の改修。cleanする場合、よりエンティティ種類数が減るため、それに応じてVQA実験時の対象エンティティも絞られる。今回はoriginに対する実験ということで、cleanは行わない。時間があまりそうであれば行う。
# TODO: 最終的なidsのjsonは、wikdata.jsonではなく、wikidata_with_commons.jsonを使うが、名前が分かりにくいのでリネームの必要あり
# TODO: ここもごちゃごちゃしているので、整理する

def main():
    start_index, end_index = 0, 5000
    categories = [sys.argv[1]]
    mode = sys.argv[2]
    if len(sys.argv) >= 4:
        start_index = int(sys.argv[3])
        end_index = int(sys.argv[4])
    # categories = ["aircraft"]
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    # mode = "filter_img"
    for category in categories:
        print(category)
        if mode == "relation":
            # カテゴリのwikidata idsを取得する
            extract_wikidata_ids_by_category(category)
            # カテゴリのwikidata relationsを取得する
            extract_wikidata_relations_by_category(category)
        if mode == "filter_img":
            # "image" と"Commons category"のどちらかが存在するエンティティのみを抽出し、wikidata_with_commons.jsonを作成する
            # ここではまだ画像の収集は行わない。記事の収集が完了し、記事の存在しないエンティティを除外した後に行った方が、無駄な画像の収集が減るため。
            filter_existing_wikimedia(category)
        if mode == "article":
            # カテゴリのwikidata_with_commons.jsonから、wikidataのURLからスクレイピングすることでwikipediaのURLを取得する
            extract_article_by_category(category, start_index, end_index)
        if mode == "filter_art":
            # 記事が存在するエンティティのみ残す
            print("Start filter_existing_wikipedia ...")
            filter_existing_wikipedia(category)
            # QA用に生成する
            print("Start create_id_to_name ...")
            create_id_to_name(category)
            # relationからtextを生成する
            print("Start relations_to_text_by_category ...")
            relations_to_text_by_category(category)
            # textをクリーニングする
            print("Start clean_relations_text_by_category ...")
            clean_relations_text_by_category(category)
        if mode == "image":
            # カテゴリのwikidata_with_commons.jsonからwikidata relationsを取得し、それぞれのエンティティのwikimediaカテゴリを取得する
            extract_images(category, start_index, end_index)
        if mode == "ids":
            create_ids_file(category)

if __name__ == "__main__":
    main()



