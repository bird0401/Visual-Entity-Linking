# experiment内の幅広いファイルで用いる定数や関数を定義する

data_dir = "/work/gk77/k77024/Visual-Entity-Linking/data"

def get_category_dir(category):
    return f"{data_dir}/{category}"

# change comment out depending on test or production
def get_gpt_output_dir(category_dir):
    return f"{category_dir}/gpt_3_output_test"
    # return f"{category_dir}/gpt_3_output"

def get_article_dir(category_dir):
    return f"{category_dir}/wikipedia"

def get_save_path(category_dir, start_idx, end_idx):
    return f"{category_dir}/qas_{start_idx}_{end_idx}.json"