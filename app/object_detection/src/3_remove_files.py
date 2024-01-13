import glob, os, re, shutil, sys

import logging
import logging.config
from yaml import safe_load

with open("../conf/logging.yml") as f:
    cfg = safe_load(f)
logging.config.dictConfig(cfg)
logger = logging.getLogger("main")


def move_from_crop_to_images(ids_dir_path):
    # 生成されたoriginの画像は必要ないので削除
    logger.info(f"Process in {ids_dir_path}")
    image_origin_paths = glob.glob(f"{ids_dir_path}/*.jpg")
    logger.info(f"len(image_origin_paths): {len(image_origin_paths)}")
    for image_origin_path in image_origin_paths:
        os.remove(image_origin_path)
    
    # cleanの実験には切り抜いた画像を利用するため、clean直下に移動
    # logger.info(f"Move from crops to imgs directory: {ids_dir_path}")
    image_crop_paths = glob.glob(f"{ids_dir_path}/crops/*/*.jpg")
    logger.info(f"len(image_crop_paths) after: {len(image_crop_paths)}")
    for image_crop_path in image_crop_paths:
        image_crop_path_split = image_crop_path.split("/")
        new_file_name = f"{image_crop_path_split[-2]}_{image_crop_path_split[-1]}"
        shutil.move(image_crop_path, f"{ids_dir_path}/{new_file_name}") 

    # cropディレクトリを削除
    if os.path.exists(f"{ids_dir_path}/crops"):
        shutil.rmtree(f"{ids_dir_path}/crops")
    
    print()


# 1体だけ検出した画像以外を削除する: 人間に関するカテゴリのみ
def remove_zero_muiti_detect_imgs(clean_dir):
    logger.info("Remove multi-detect images")
    ids_dir_paths = glob.glob(f"{clean_dir}/*")
    # cropsの下に2つ以上の階層がある場合にエラーが起こる。
    for ids_dir_path in ids_dir_paths:
        image_crop_paths = glob.glob(f"{ids_dir_path}/crops/*/*.jpg")
        logger.info(f"len(image_crop_paths) before: {len(image_crop_paths)}")

        # crop後のファイルから複数検出された画像を削除
        for image_crop_path in image_crop_paths:
            image_crop_path_split = image_crop_path.split("/")
            filename = image_crop_path_split[-1]
            dir_name = "/".join(image_crop_path_split[:-1])
            # それぞれの画像ファイルはこの正規表現に当てはまるように収集している
            # 複数検出された場合は、例えば、image_0000.jpgではimage_0000_1.jpgのようになるため、この正規表現には当てはまらない
            # image_wikipedia.jpgも存在するので、これについても考慮
            pattern_1 = re.compile(r'^image_\d{4}')
            pattern_2 = re.compile(r'^image_wikipedia')

            if not (re.match(r"image_[0-9][0-9][0-9][0-9].jpg", filename) or re.match(r"image_wikipedia.jpg", filename)):
                # 複数検出される場合は必ず2つ以上のファイルが生成される。そのため、2つ目のファイルのパスを取得し削除
                if pattern_1.match(filename):
                    another_file_name = f"{filename[:10]}{filename[-4:]}"
                elif pattern_2.match(filename):
                    another_file_name = f"{filename[:15]}{filename[-4:]}"
                # print(another_file_name)
                another_path = f"{dir_name}/{another_file_name}"
                os.remove(image_crop_path)
                if os.path.exists(another_path):
                    os.remove(another_path)

        move_from_crop_to_images(ids_dir_path)
        print()


# 物体検出されなかった画像を削除する
def remove_zero_detect_imgs(clean_dir):
    logger.info("Remove zero-detect images")
    logger.info(f"clean_dir: {clean_dir}")
    ids_dir_paths = glob.glob(f"{clean_dir}/*")
    logger.info(f"num ids in {clean_dir} directory: {len(ids_dir_paths)}")
    for ids_dir_path in ids_dir_paths:
        move_from_crop_to_images(ids_dir_path)
        # 必要無くなった処理のため一旦コメントアウト
        # ここから
        # image_crop_paths = glob.glob(f"{ids_dir_path}/crops/*/*.jpg")
        # image_origin_paths = glob.glob(f"{ids_dir_path}/*.jpg")

        # crop_filenames = []
        # for image_crop_path in image_crop_paths:
        #     filename = os.path.basename(image_crop_path)
        #     crop_filenames.append(filename)

        # # Remove no detect files
        # remove_cnt = 0
        # logger.info(f"len(image_origin_paths): {len(image_origin_paths)}")
        # for image_origin_path in image_origin_paths:
        #     origin_filename = os.path.basename(image_origin_path)
        #     if origin_filename not in crop_filenames:
        #         # logger.info(f"remove: {image_origin_path}")
        #         remove_cnt += 1
        #         # os.remove(path_origin) # TODO: 削除するのは危険なので一旦コメントアウト
        # logger.info(f"remove_cnt: {remove_cnt}")
        # ここまで


# 注意。一度実行するとファイル群が削除されるので、ここで実験する前にバックアップを作っておく
# CAUTION: MUST NOT EXECUTE TWICE IN THE SAME CATEGORY TO AVOID DELETING ALL IMAGES
def main():
    # categories = ["aircraft", "athlete", "bird", "bread", "car", "director", "dog", "us_politician"]
    categories = ["us_politician"]
    for category in categories:
        # category = sys.argv[1]
        clean_dir = f"../../../data/{category}/images/clean"

        # birdでイラストなどがあるため削除。
        # TODO: わざわざイラストを削除する必要性はないのかもしれない、要検討
        if category in ["aircraft", "bird", "bread", "car"]: 
            remove_zero_detect_imgs(clean_dir) 
        
        # 画像中の主役のエンティティがどれかわからない場合は削除
        # 人や犬のカテゴリに対して適用
        elif category in ["athlete", "dog", "director", "us_politician"]: 
            remove_zero_muiti_detect_imgs(clean_dir)


if __name__ == "__main__":
    main()
