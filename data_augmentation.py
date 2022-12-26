from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any
import json
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


    def __post_init__(self):
        if self.window_size_after_augmentation is None:
            raise ValueError("You should specify windowsize that the data is arranged after augmentation.")


def augment_line_to_my_dob_is(data):
    pass


def aug_data(args):
    # 这里已经事先把相应的训练中应该出现的window_size分割好了
    data_before_auged = []
    auged_data = []
    input_file_path = args.input_data_path
    window_size = args.window_size_after_augmentation
    aug_density = args.augmentation_density
    fin = open(input_file_path, "r")
    data = json.load(fin)
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
    # view the data
    for a_data in maybe_have_pre_data:
        flatten_label = []
        bottom_line = []
        splitted_words = a_data["order"][-1][1].split(" ")
        label = a_data["label"][-1]
        for a_label in label:
            flatten_label.extend(a_label)
        for a_word_index, a_word in enumerate(splitted_words):
            if a_word_index in flatten_label:
                a_word = hl_format.format(a_word)
            bottom_line.append(a_word)
        print(" ".join(bottom_line), end="")
        input("")
            


    # augment the all words line:
    for a_data in all_words_data:
        pass
        
        
            
    import pdb;pdb.set_trace()
    

        
            
        
def main():
    parser = HfArgumentParser((CustomArguments))
    custom_args = parser.parse_args_into_dataclasses()[0]
    auged_data = aug_data(custom_args)


if __name__=="__main__":
    main()
