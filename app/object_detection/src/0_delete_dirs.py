import glob, shutil

def main():
    paths = glob.glob("../data_*/imgs/*/crops")
    # for path in paths:
    #     print(path)
    for path in paths:
        shutil.rmtree(path)

if __name__=="__main__":
    main()