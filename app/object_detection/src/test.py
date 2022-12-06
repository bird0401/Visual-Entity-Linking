from collections import defaultdict
# d = defaultdict(dict)
d = {"1":1, "2":2}
dd={}
dd["a"]=d
print(dd)
print(dd["a"]["1"])