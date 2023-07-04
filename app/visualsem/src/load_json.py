import json

# import logging
# import logging.config
# from yaml import safe_load

# with open("../conf/logging.yml") as f:
#     cfg = safe_load(f)
# logging.config.dictConfig(cfg)
# logger = logging.getLogger("main")

def main():
    nodes_file = "../datasets/tuples.v2.json"
    # nodes_file = "../datasets/nodes.v2.json"
    with open(nodes_file) as f:
        nodes = json.load(f)
    # node_id = "bn:00018323n" # president
    # node_id = "bn:00073045n"
    # node_id = "bn:00015267n" # dog
    node_id = "bn:00002275n" # airplane
    # print(nodes[node_id])
    relations = set()
    for dic in nodes[node_id]:
        s = dic["s"]
        r = dic["r"]
        r_id = dic["r_id"]
        relations.add(r)
        # print(node_id, r, s)
        if r == "HasA":
            print(node_id, r, s)
        # if s == "bn:00022649n":
        #     print(node_id, r, s)
    print(relations)


if __name__ == "__main__":
    main()




