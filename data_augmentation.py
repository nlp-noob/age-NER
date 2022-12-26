from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
import json
import random
import copy
from transformers import (
    HfArgumentParser,
)

hl_format = "\033[7m{}\033[0m"


@dataclass
class CustomArguments:
    window_size_after_augmentation: int = field(
        default=None,
        metadata={
            "help": (
                "In order to reduce the duplicated data ouside the augmentation data,"
                "The data is split into the window size for training beforehand."
            )
        },
    )

    input_data_path: str = field(
        default=None,
        metadata={
            "help": (
                "the input data path to be auged."
            )
        },
    )

    augmentation_density: int = field(
        default=None,
        metadata={
            "help": (
                "the auged density of the auged data."
            )
        },
    )

    template_file_path: str = field(
        default=None,
        metadata={
            "help": (
                "the template file path."
            )
        },
    )

    def __post_init__(self):
        if self.window_size_after_augmentation is None:
            raise ValueError("You should specify windowsize that the data is arranged after augmentation.")


def _clear_words_list_with_labels(words_list, labels): 
    for label in labels:
        for a_label_index, a_label in enumerate(label):
            if a_label_index == 0:
                words_list[a_label] = "{}"
            else:
                words_list[a_label] = "I-{}"
    result_words_list = []
    for a_word in words_list:
        if a_word == "I-{}":
            continue
        else:
            result_words_list.append(a_word)
    return result_words_list


def _exchange_labeled_words_in_data(data_to_be_append, pieces_for_change, label_in_pieces):
    bottom_line = data_to_be_append["order"][-1][1]
    bottom_words = bottom_line.split(" ")
    origin_labels = data_to_be_append["label"][-1]
    new_labels = []
    cleared_bottom_words = _clear_words_list_with_labels(bottom_words, origin_labels)
    changed_words = []
    change_cnt = 0
    for a_word in cleared_bottom_words:
        a_label_piece = []
        if a_word == "{}":
            a_piece_for_change = pieces_for_change[change_cnt] 
            a_label_in_piece = label_in_pieces[change_cnt]
            for change_word_index, change_word in enumerate(a_piece_for_change):
                if change_word_index in a_label_in_piece:
                    a_label_piece.append(len(changed_words))
                changed_words.append(change_word)
            change_cnt += 1
        else:
            changed_words.append(a_word)
        new_labels.append(a_label_piece)

    data_to_be_append["order"][-1][1] = " ".join(changed_words)
    data_to_be_append["label"][-1] = new_labels
    return data_to_be_append


def augment_line_randomly(args, a_data):
    # Use the function to augment a data that have no pre-expression
    # So if a data have pre-expresion, you should kill it first
    auged_data = []
    augment_density = args.augmentation_density
    if augment_density%2 != 0:
        agment_density += 1
    ftemp = open(args.template_file_path, "r")
    template_dict = json.load(ftemp)
    ftemp.close()
    for i in range(augment_density):
        data_to_be_append = copy.deepcopy(a_data)
        origin_labels = data_to_be_append["label"][-1]
        pieces_for_change = []
        label_in_pieces = []

        # get the random format
        if i % 2 == 0:
            aug_mode = "date"
        else:
            aug_mode = "age"
        templates = template_dict[aug_mode + "_templates"]
        formats = template_dict[aug_mode + "_formats"]
        id2key = template_dict["id2key"]
        random_template = templates[random.randint(0, len(templates)-1)]
        random_format = formats[random.randint(0, len(formats)-1)]

        # the same user is tend to use the same punctuation to split the words.
        random_punc = template_dict[id2key["0"]][random.randint(0, len(template_dict[id2key["0"]])-1)]

        # get pieces equals to the cnt of the labels in bottom line
        for a_label in origin_labels:
            temp_piece = []
            temp_label_in_piece = []
            for template_index, template_word in enumerate(random_template):
                if template_word == "{}":
                    for format_index, format_id in enumerate(random_format):
                        if format_id != "0":
                            random_word_format = template_dict[id2key[format_id]][random.randint(0, len(template_dict[id2key[format_id]])-1)]
                        else:
                            random_word_format = random_punc
                        temp_piece.append(random_word_format)
                        temp_label_in_piece.append(template_index + format_index)
                else:
                    temp_piece.append(template_word)
            pieces_for_change.append(temp_piece)
            label_in_pieces.append(temp_label_in_piece)

        # exchange the labeled word in data_to_be_append
        data_to_be_append = _exchange_labeled_words_in_data(data_to_be_append, pieces_for_change, label_in_pieces)
        auged_data.append(data_to_be_append)
    return auged_data


def clear_may_be_have_pre_data(may_be_have_pre_data, args):
    ftemp = open(args.template_file_path, "r")
    template_dict = json.load(ftemp)
    ftemp.close()
    pre_expressions = template_dict["pre_expressions"]
    data_cleared = copy.deepcopy(may_be_have_pre_data)
    bottom_line = may_be_have_pre_data["order"][-1][1]
    all_pre_expressions_in_line = []
    for a_pre_expression in pre_expressions:
        if a_pre_expression in bottom_line:
            all_pre_expressions_in_line.append(a_pre_expression)
    if len(all_pre_expressions_in_line) == 0:
        return False

    flatten_expresions_words = []
    for a_expression in all_pre_expressions_in_line:
        flatten_expresions_words.extend(a_expression.split(" "))

    bottom_line_words = bottom_line.split(" ")
    labels = may_be_have_pre_data["label"][-1]
    flatten_labels = []
    for a_label in labels:
        for a_label_index in a_label:
            flatten_labels.append(a_label_index)
    pre_indexs = []
    for a_label in labels:
        pre_index_for_a_label = []
        begin_label = a_label[0]
        up_index = 1
        while(True):
            now_index = begin_label - up_index
            if (now_index < 0 or 
                now_index in flatten_labels or 
                bottom_line_words[now_index] not in flatten_expresions_words):
                break
            else:
                pre_index_for_a_label.append(now_index)
                up_index += 1
        pre_index_for_a_label.reverse()
        pre_indexs.append(pre_index_for_a_label)
    new_labels = []
    new_bottom_line_words = []
    mirror_words = []
    for a_word in bottom_line_words:
        mirror_words.append("O")
    for label, pre in zip(labels, pre_indexs):
        for a_label_index, a_label in enumerate(label):
            if a_label_index == 0:
                mirror_words[a_label] = "B-DATE"
            else:
                mirror_words[a_label] = "I-DATE"
        for a_pre_index, a_pre in enumerate(pre):
            if a_pre_index == 0:
                mirror_words[a_pre] = "B-PRE"
            else:
                mirror_words[a_pre] = "I-PRE"

    new_label_piece = []
    for a_word_index, a_word in enumerate(bottom_line_words):
        mirror_word = mirror_words[a_word_index]
        if mirror_word == "B-PRE" or mirror_word == "I-PRE":
            continue
        elif mirror_word == "O":
            new_bottom_line_words.append(a_word)
        elif mirror_word == "B-DATE":
            if len(new_label_piece) > 0:
                new_labels.append(new_label_piece)
                new_label_piece = []
            new_label_piece.append(len(new_bottom_line_words))
            new_bottom_line_words.append(a_word)
        elif mirror_word == "I-DATE":
            new_label_piece.append(len(new_bottom_line_words))
            new_bottom_line_words.append(a_word)
    if len(new_label_piece) > 0:
        new_labels.append(new_label_piece)

    data_cleared["order"][-1][1] = " ".join(new_bottom_line_words)
    data_cleared["label"][-1] = new_labels
    return data_cleared




def aug_data(args):
    # 这里已经事先把相应的训练中应该出现的window_size分割好了
    data_before_auged = []
    auged_data = []
    input_file_path = args.input_data_path
    window_size = args.window_size_after_augmentation
    aug_density = args.augmentation_density
    fin = open(input_file_path, "r")
    data = json.load(fin)
    fin.close()
    for an_order in data:
        for line_index, line in enumerate(an_order["order"]):
            temp_order = {
                          "pairNO": an_order["pairNO"], 
                          "orderNO": an_order["orderNO"],
                          "order" : None,
                          "label" : None,
                         }
            if not line[0]:
                # jump the advisor lines
                continue
            else:
                temp_input = [copy.deepcopy(line)]
                temp_label = [copy.deepcopy(an_order["label"][line_index])]
                for i in range(window_size):
                    up_index = i + 1
                    now_index = line_index - up_index
                    if now_index < 0:
                        break
                    else:
                        temp_input.append(copy.deepcopy(an_order["order"][now_index]))
                        temp_label.append(copy.deepcopy(an_order["label"][now_index]))
                temp_input.reverse()
                temp_label.reverse()
                temp_order["order"] = temp_input
                temp_order["label"] = temp_label
                data_before_auged.append(temp_order)
    print("**"*20)
    print("The data before auged have {} inputs".format(len(data_before_auged)))
    print("**"*20)
    #########################################################
    # augment data in bottom line (reduce the duplicated data)
    # The data have two cases bellow generally:
    # 1. all the words in line is the labeled.(e.g. March 272002)
    # 2. the labeled words have the pre expression.(e.g. with my ex girlfriend Sandy Dob may 25 )
    # So the data augmentation process is just like bellow
    # 1. Find out if all words in line are the labeled words.(split into two cases)
    #    There is not any problem of augment the "all words" type line.
    # 2. By using a list of key words to try to findout the words which may be the pre-expression for dob.
    # 3. There is some lines' pre-expresion is not find, just check them out and add the key words to get it.
    #########################################################
    all_words_data = []
    maybe_have_pre_data = []
    for a_data in data_before_auged:
        bottom_label = a_data["label"][-1]
        bottom_line = a_data["order"][-1][1]
        # append the original data
        auged_data.append(copy.deepcopy(a_data))
        if len(bottom_label) == 0:
            # jump the data that have no label in the bottom line.
            continue
        else:
            label_index_cnt = 0
            for a_label in bottom_label:
                label_index_cnt += len(a_label)
            if label_index_cnt == len(bottom_line.split(" ")):
                all_words_data.append(copy.deepcopy(a_data))
            else:
                maybe_have_pre_data.append(copy.deepcopy(a_data))
    # # view the data
    # for a_data in maybe_have_pre_data:
    #     flatten_label = []
    #     bottom_line = []
    #     splitted_words = a_data["order"][-1][1].split(" ")
    #     label = a_data["label"][-1]
    #     for a_label in label:
    #         flatten_label.extend(a_label)
    #     for a_word_index, a_word in enumerate(splitted_words):
    #         if a_word_index in flatten_label:
    #             a_word = hl_format.format(a_word)
    #         bottom_line.append(a_word)
    #     print(" ".join(bottom_line), end="")
    #     input("")
            


    # augment the all words line:
    for a_data in all_words_data:
        new_datas = augment_line_randomly(args, copy.deepcopy(a_data))
        auged_data.extend(new_datas)

    uncleared_data = []
    cleared_data = []
    # clear the data that maybe have pre 
    for process_num, a_data in enumerate(maybe_have_pre_data):
        a_cleared_data = clear_may_be_have_pre_data(a_data, args)
        if a_cleared_data == False:
            uncleared_data.append(a_data)
        else:
            cleared_data.append(a_cleared_data)
    print("the len of the uncleared data is: {}".format(len(uncleared_data)))
    print("the len of the cleared data is:   {}".format(len(cleared_data)))

    # augmentation on the uncleared data
    for a_data in uncleared_data:
        new_datas = augment_line_randomly(args, copy.deepcopy(a_data))
        auged_data.extend(new_datas)

    # augmentation on the cleared data
    for a_data in cleared_data:
        new_datas = augment_line_randomly(args, copy.deepcopy(a_data))
        auged_data.extend(new_datas)
    print("**"*20)
    print("The data after auged have {} inputs".format(len(auged_data)))
    print("**"*20)
    return auged_data
            
        
def main():
    parser = HfArgumentParser((CustomArguments))
    custom_args = parser.parse_args_into_dataclasses()[0]
    auged_data = aug_data(custom_args)
    # get the path of output file
    input_data_path = custom_args.input_data_path
    file_path_list = input_data_path.split("/")
    file_name = file_path_list[-1]
    new_file_name = "augmented_win{}_dens{}_".format(custom_args.window_size_after_augmentation, custom_args.augmentation_density) + file_name
    del(file_path_list[-1])
    file_path_list.append(new_file_name)
    output_file_path = "/".join(file_path_list)
    json_str = json.dumps(auged_data, indent=2)
    fout = open(output_file_path, "w")
    fout.write(json_str)
    print("the file is written to path:")
    print(output_file_path)


if __name__=="__main__":
    main()
