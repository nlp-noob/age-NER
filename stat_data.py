import json


data_path = "data/user_index_data/tagged_raw_date_data.json"


def stat_data(data_path):
    jf = open(data_path, "r")
    data = json.load(jf)
    jf.close()
    key_list = list(data[0].keys())
    user_label_stat = {}
    user_label_stat_order_indexs = {}
    have_label_data_cnt = 0
    for order_index, order in enumerate(data):
        if order["user_index"] in list(user_label_stat.keys()):
            user_label_stat[order["user_index"]] += 1
            user_label_stat_order_indexs[order["user_index"]].append(order_index)
        else:
            user_label_stat[order["user_index"]] = 0
            user_label_stat_order_indexs[order["user_index"]] = [order_index]
        for label in order["label"]:
            if len(label) > 0:
                have_label_data_cnt += 1
                break

    print(user_label_stat)
    print("There are {} orders have label.".format(have_label_data_cnt))
    print("0 user index label in labeled order ratio is {}".format(user_label_stat[0]/have_label_data_cnt))
    return user_label_stat_order_indexs


def main():
    jf = open(data_path, "r")
    data = json.load(jf)
    jf.close()
    key_list = list(data[0].keys())
    user_label_stat = {}
    have_label_data_cnt = 0
    for order in data:
        if order["user_index"] in list(user_label_stat.keys()):
            user_label_stat[order["user_index"]] += 1
        else:
            user_label_stat[order["user_index"]] = 0
        for label in order["label"]:
            if len(label) > 0:
                have_label_data_cnt += 1
                break

    print(user_label_stat)
    print("There are {} orders have label.".format(have_label_data_cnt))
    print("0 user index label in labeled order ratio is {}".format(user_label_stat[0]/have_label_data_cnt))


if __name__ == "__main__":
    main()
