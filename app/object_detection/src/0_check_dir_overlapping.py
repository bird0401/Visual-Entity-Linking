import glob

target_dirs = ["data_us_politician", "data_us_politician_second", "data_us_politician_third"]
dirs = [set(), set(), set()]
for i, target_dir in enumerate(target_dirs):
    full_paths = glob.glob(f"../{target_dir}/imgs/*")
    for full_path in full_paths:
        dirs[i].add(full_path.split("/")[-1])
common = dirs[0] & dirs[1] & dirs[2]
print(len(common))
print(common)

# test = set()
# test.add("Q374162")
# print(test & dirs[0])
# print(test & dirs[1])
# print(test & dirs[2])