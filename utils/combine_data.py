import json


data_file1 = "./data/train_data/train_data0000.json"
data_file2 = "./data/valid_data/valid_data0000.json"
out_file = "./data/user_index_data/raw_date_data.json"


def main():
    out_data = []
    df1 = open(data_file1, "r")
    data1 = json.load(df1)
    df1.close()
    df2 = open(data_file2, "r")
    data2 = json.load(df2)
    df2.close()
    out_data.extend(data1)
    out_data.extend(data2)
    fout = open(out_file, "w")
    json_str = json.dumps(out_data, indent=2)
    fout.write(json_str)
    fout.close()
    print("Write Success")
    print("the data lenth = {}".format(len(out_data)))


if __name__ == "__main__":
    main()
