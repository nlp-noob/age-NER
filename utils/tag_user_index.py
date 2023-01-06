import json
import copy


class UserTagger():
    def __init__(self, data_file_path, user_template_path):
        self.new_user_template_path = "new_" + user_template_path
        ftemp = open(user_template_path, "r")
        self.template_dict = json.load(ftemp)
        ftemp.close()
        fdata = open(data_file_path, "r")
        self.data_list = json.load(fdata)
        fdata.close()
        self.tagged_data_list = None

        file_path_list = data_file_path.split("/")
        file_path_list[-1] = "tagged_" + file_path_list[-1]
        self.out_data_path = "/".join(file_path_list)
        
    def _pattern_in_line(self, line):
        """
            return the tail_pattern or the head_pattern
        """
        for key in list(self.template_dict.keys()):
            for pattern in self.template_dict[key]:
                if pattern in line:
                    return key
        return False

    def _display_an_order(self, order):
        hl_text = "\033[7m{}\033[0m"
        for line_index, line in enumerate(order["order"]):
            line_label = order["label"][line_index]
            line_character = "[USER]" if line[0] else "[ADVI]"
            line_text = line[1]
            line_text_words = line_text.split(" ")
            # hl
            for labels in line_label:
                for label in labels:
                    line_text_words[label] = hl_text.format(line_text_words[label])
            line_text = " ".join(line_text_words)
            display_line =  str(line_index) + "\t" + line_character + "\t\t" + line_text
            print(display_line)

    def _stat_data_with_template(self):
        # general count
        label_count = {}
        orders_with_label_cnt = 0
        orders_no_label_cnt = 0
        have_pattern_cnt = 0
        labeled_orders_no_pattern = []
        for order in self.data_list:
            order_label_cnt = 0

            have_label = False
            have_pattern = False
            for label_index, label in enumerate(order["label"]):
                line = order["order"][label_index][1]
                if self._pattern_in_line(line):
                    have_pattern = True

                order_label_cnt += len(label)
                if len(label) > 0:
                    have_label = True

            if have_label:
                if have_pattern:
                    have_pattern_cnt += 1
                else:
                    labeled_orders_no_pattern.append(order)
                orders_with_label_cnt += 1

            else:
                orders_no_label_cnt += 1

            if order_label_cnt not in list(label_count.keys()):
                label_count[order_label_cnt] = 0
            else:
                label_count[order_label_cnt] += 1

        print("*****************************************")
        print("There are totally {} order_data.".format(len(self.data_list)))
        print("-----------------------------")
        print("The label count distribution:")
        print(label_count)
        print("-----------------------------")
        print("There are {} no_label_orders".format(orders_no_label_cnt))
        print("-----------------------------")
        print("There are {} have_label_orders".format(orders_with_label_cnt))
        print("-----------------------------")
        print("There are {} labeled orders with patterns".format(have_pattern_cnt))
        print("There are {} labeled orders no patterns".format(len(labeled_orders_no_pattern)))
        print("The ratio is {}".format(have_pattern_cnt / orders_with_label_cnt))
        print("*****************************************")
        return labeled_orders_no_pattern

    def _write_pattern_template(self):
        fout = open(self.new_user_template_path, "w")
        json_str = json.dumps(self.template_dict, indent=2)
        fout.write(json_str)
        fout.close()

    def _get_right_input_pattern(self):
        while(True):
            print("**"*20)
            print("Please input the pattern you wanto insert like this:")
            print("insert {head/tail} {content}")
            print("or input the char j means there is no pattern in this order, then this order would not be shown next time.")
            user_input = input()
            input_words = user_input.split(" ")
            if len(input_words) == 1 and input_words[0] == "j":
                return False
            elif len(input_words) > 3 and input_words[0] == "insert" and input_words[1] in ["head", "tail"]:
                insert_pattern = " ".join(input_words[2:])
                self.template_dict[input_words[1]+"_template"].append(insert_pattern)
                self._write_pattern_template()
                return True
            else:
                input("Wrong Input!!!! Press enter to re-input.")

    def _get_right_input_label(self, len_label):
        while(True):
            print("**"*20)
            print("please input the index of the user label.")
            print("-1 for no user, 0-n for index.")
            print("**"*20)
            user_input_str = input()
            if user_input_str == "-1":
                return -1
            elif not user_input_str.isdigit():
                input("Wrong input !! Please press any key to re-input.")
                continue
            else:
                input_int = int(user_input_str)
                if input_int >= len_label:
                    input("Wrong input !! Please press any key to re-input.")
                    continue
                else:
                    return input_int

    def _fix_pattern(self):
        no_pattern_cnt = 0
        hl_text = "\033[7m{}\033[0m"
        while(True):
            labeled_orders_no_pattern = self._stat_data_with_template()
            print("There are {} remaining orders.".format(len(labeled_orders_no_pattern)))
            if len(labeled_orders_no_pattern) == no_pattern_cnt:
                break
            # jump the no pattern order next time
            for order in labeled_orders_no_pattern[no_pattern_cnt:]:
                self._display_an_order(order)
                insert_a_pattern = self._get_right_input_pattern()
                if insert_a_pattern:
                    break
                else:
                    no_pattern_cnt += 1
                    break
        print(hl_text.format("You have finish the pattern insert process"))
        self._stat_data_with_template()
        input("Please check the ratio.")

    def _pretag_with_patterns(self):
        for order in self.data_list:
            all_labels = []

    def _write_tagged_data(self):
        ftag = open(self.out_data_path, "w")
        json_str = json.dumps(self.tagged_data_list, indent=2)
        ftag.write(json_str)
        ftag.close()
        print("Write Success")

    def _tag_mannually(self, save_every=20):
        self.tagged_data_list = copy.deepcopy(self.data_list)
        for process_index, order in enumerate(self.data_list):
            print("------------------------------------------")
            print("you are processing {}/{}".format(process_index + 1, len(self.data_list)))
            print("------------------------------------------")
            label_len = 0
            for label in order["label"]:
                label_len += len(label)
            if label_len == 0:
                self.tagged_data_list[process_index]["user_index"] = -1
                print("Jump the {} order without label")
                continue
            self._display_an_order(order)
            input_int = self._get_right_input_label(label_len)
            self.tagged_data_list[process_index]["user_index"] = input_int
            if process_index % save_every == 0:
                self._write_tagged_data()
        self._write_tagged_data()

    def tag_user_index(self, try_to_fix_patterns=False):
        if try_to_fix_patterns:
            self._fix_pattern()
        # self._pretag_with_patterns()
        self._tag_mannually()

        


def test():
    pass


if __name__ == "__main__":
    test()
