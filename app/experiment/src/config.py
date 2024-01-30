# experiment内の幅広いファイルで用いる定数や関数を定義する

data_dir = "/work/gk77/k77024/Visual-Entity-Linking/data"

patterns = [
    {"name": False, "article": False, "relations": False, "confidence": False}, 
    {"name": True, "article": False, "relations": False, "confidence": False}, 
    {"name": True, "article": True, "relations": False, "confidence": False}, 
    {"name": True, "article": False, "relations": True, "confidence": False}, 
    {"name": True, "article": True, "relations": True, "confidence": False}, 
    # {"name": True, "article": True, "relations": True, "confidence": True}, 
]

def get_category_dir(category):
    return f"{data_dir}/{category}"

# change comment out depending on test or production
def get_gpt_output_dir(category):
    category_dir = get_category_dir(category)
    return f"{category_dir}/gpt_3_output_test"
    # return f"{category_dir}/gpt_3_output"

def get_article_dir(category):
    category_dir = get_category_dir(category)
    return f"{category_dir}/wikipedia"

def get_entity_to_qas_path(category, start_idx, end_idx):
    category_dir = get_category_dir(category)
    return f"{category_dir}/qas_{start_idx}_{end_idx}.json"

def get_entity_to_qas_bem_path(category, start_idx, end_idx):
    category_dir = get_category_dir(category)
    return f"{category_dir}/qas_{start_idx}_{end_idx}_bem.json"

