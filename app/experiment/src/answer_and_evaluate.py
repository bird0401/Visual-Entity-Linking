

def main():
    logger.info("Start answer_by_categories ...")

    # For test
    category = "aircraft" 
    start_idx = 0
    end_idx = 3
    mode = "oracle"
    
    # category = sys.argv[1] # "aircraft"
    # start_idx = int(sys.argv[2])
    # end_idx = int(sys.argv[3])
    # mode = sys.argv[4] # "oracle" or "pred"

    answer_by_category(category, mode=mode, start_idx=start_idx, end_idx=end_idx)



if __name__ == "__main__":
    main()