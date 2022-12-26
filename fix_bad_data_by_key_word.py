import json
import readline

# words that indicate that the line maybe the dob line
KEYWORDS_LIST = ["DOB", "dob", "Jan", "Feb", "April", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
check_mode = "direct"
# by bad_cases / by direct
DATA_PATH = "./data/large_json/pretaggedempty.json"
OUTPUT_PATH = "./data/large_json/pretaggedempty_fixxed.json"
SELECTED_OUT_PATH = "./data/large_json/selected_data.json"
BADCASE_FILE = "badcases_train/dslim_bert-large-NER_win3_cosine/bad_case_for_step_00002400.txt"
FORBIDDEN_WORDS = ["er", "ke"]
hl_format = "\033[7m{}\033[0m"
save_every_step = 200

def number_words_in_sentence(sentence, label):
    word_list = sentence.split()
    words_str = ""
    index_str = ""
    for index in range(len(word_list)):
        space_bias = abs(len(word_list[index])-len(str(index)))
        word_index_is_in_label = False
        for a_label in label:
            if index in a_label:
                word_index_is_in_label = True
                break
        
        if(len(word_list[index])>len(str(index))):
            if word_index_is_in_label:
                word_list[index] = hl_format.format(word_list[index])
            words_str = words_str + word_list[index] + "\t" 
            index_str = index_str + str(index) + " "*space_bias + "\t" 
        else:
            if word_index_is_in_label:
                word_list[index] = hl_format.format(word_list[index])
            words_str = words_str + word_list[index] + " "*space_bias + "\t"
            index_str = index_str + str(index) + "\t" 
    print(words_str)
    print(index_str)

def search_words(data_to_fix, words):
    if len(words)==1 and len(words[0])<=1:
        return []
    elif len(words)==1 and words[0] in FORBIDDEN_WORDS:
        return []
    index_list = []
    for order_index, order in enumerate(data_to_fix):
        for line_index, line in enumerate(order["order"]):
            if not line[0]:
                continue
            # words全部都在这行才算
            output_index_flag = True
            for a_word in words:
                if not a_word in line[1]:
                    output_index_flag = False
            if output_index_flag:
                index_list.append([order_index,line_index])
    if len(index_list)>10:
        print(words)
        raise ValueError("There too manny results for tagging plz check if the words above is too short") 
    if len(index_list)==0:
        return False 
    else:
        return index_list


def _line_have_keywords(line):
    line_have_keyword = False
    for keyword in KEYWORDS_LIST:
        if keyword in line:
            line_have_keyword = True
            break
    return line_have_keyword


def _line_have_num(line):
    line_have_num = False
    for a_char in line:
        if a_char.isdigit():
            line_have_num = True
            break
    return line_have_num


def get_indexs_for_data_check(data_to_fix):
    result_list = []
    for order_index, order in enumerate(data_to_fix):
        for line_index, line in enumerate(order["order"]):
            if not line[0]:
                continue
            if len(order["label"][line_index]) > 0:
                result_list.append([order_index, line_index])
            elif(_line_have_num(line[1])):
                result_list.append([order_index, line_index])
            elif(_line_have_keywords(line[1])):
                result_list.append([order_index, line_index])
    return result_list

     
def check_right_list(check_list, input_mode):
    for item in check_list:
        if(str(type(item))!="<class 'list'>"):
            return False
        elif(len(item)==0):
            return False
        for sub_item in item:
            if(str(type(sub_item))!="<class 'int'>"):
                return False
    check_list_changed = []
    if input_mode=="simple_input":
        for tuple_label in check_list:
            temp_list = []
            begin_ind = tuple_label[0]
            end_ind = tuple_label[1]
            temp_ind = begin_ind
            while(True):
                if temp_ind > end_ind:
                    break
                temp_list.append(temp_ind)
                temp_ind = temp_ind + 1
            check_list_changed.append(temp_list)
        return check_list_changed
    else:
        return check_list


def main():
    with open(DATA_PATH, "r") as jf:
        data_to_fix = json.load(jf)
        jf.close()

    if check_mode=="bad_cases":
        # get bad words:
        bad_words_line_indexs = []
        all_words_pattern = "all_words:\t" 
        with open(BADCASE_FILE, "r") as bf:
            bad_data = bf.readlines()
            for order_index, line in enumerate(bad_data):
                if all_words_pattern in line:
                    all_words = line.strip().split("\t")[1:]
                    line_index = search_words(data_to_fix, all_words)
                    if line_index:
                        bad_words_line_indexs.extend(line_index)
                    elif line_index!=False:
                        continue
                    else:
                        print(all_words)
                        raise ValueError("There is not corresponding wrong words above in the data, please check it manually!!!") 
    else:
        bad_words_line_indexs = get_indexs_for_data_check(data_to_fix)

    quit_flag = False
    selected_order_indexs = []
    # show and fix the bad word index
    now_step = 0
    for bad_fix_progress, bad_word_index in enumerate(bad_words_line_indexs):
        now_step += 1
        order_index = bad_word_index[0]
        line_index = bad_word_index[1]
        label = data_to_fix[order_index]["label"][line_index]
        label_fix = []
        while(True):
            input_mode = None
            print("=="*30)
            print("processing bad_data \t{}/{}".format(bad_fix_progress+1, len(bad_words_line_indexs)))
            print("=="*30)
            number_words_in_sentence(data_to_fix[order_index]["order"][line_index][1], label)
            print(label)
            print("label the PER in the sentence like this: [[0,1,2],[4,5,6]]")
            print("or you can specify the label by indicate the begin and end index like this: s [[0,2],[4,6]]")
            new_label_list = input("please input the new labels:") 
            get_mode = new_label_list.split()
            if len(get_mode) >= 2 and get_mode[0]=="s":
                input_mode = "simple_input"
                new_label_list = new_label_list[2:]
            else:
                input_mode = "raw_input"
            enter_list = None
            try:
                enter_list = json.loads(new_label_list)
            except:
                print("wrong json typr")
            finally:
                if str(type(enter_list))=="<class 'list'>":
                    if(len(enter_list)==0):
                        label_fix = []
                        print("=="*20)
                        print("You insert an empty label list")
                        print("=="*20)
                        break
                    elif(check_right_list(enter_list, input_mode)):
                        label_fix = check_right_list(enter_list, input_mode)
                        print("=="*20)
                        print("You insert a list of label:")
                        print(label_fix)
                        print("=="*20)
                        break
                if new_label_list == "j":
                    label_fix = label
                    break
                elif new_label_list == "quit":
                    quit_flag = True    
                    break
                else:
                    print("**"*20)
                    print("Wrong input!!!")
                    print("you should enter a list of label or just enter \"j\" to jump(empty label)")
                    print("To quit and save, enter: \"quit\"")
                    print("**"*20)
            if quit_flag:
                break
            
        if quit_flag:
            break
        else:
            # change done
            if data_to_fix[order_index]["label"][line_index] != label_fix and order_index not in selected_order_indexs:
                # save the selected order for augmentetion
                selected_order_indexs.append(order_index)
            data_to_fix[order_index]["label"][line_index] = label_fix
        if now_step % save_every_step == 0:
            selected_data_for_aug = []
            for selected_index in selected_order_indexs:
                selected_data_for_aug.append(data_to_fix[selected_index])
            json_str_aug = json.dumps(selected_data_for_aug, indent=2)
            with open(SELECTED_OUT_PATH, "w") as sfout:
                sfout.write(json_str_aug)
                print("File has been saved to the path: {}".format(SELECTED_OUT_PATH))
                sfout.close()
            json_str = json.dumps(data_to_fix, indent=2)
            with open(OUTPUT_PATH, "w") as fout:
                fout.write(json_str)
                print("File has been saved to the path: {}".format(OUTPUT_PATH))
                fout.close()
    import pdb;pdb.set_trace()
    selected_data_for_aug = []
    for selected_index in selected_order_indexs:
        selected_data_for_aug.append(data_to_fix[selected_index])
    json_str_aug = json.dumps(selected_data_for_aug, indent=2)
    with open(SELECTED_OUT_PATH, "w") as sfout:
        sfout.write(json_str_aug)
        print("File has been saved to the path: {}".format(SELECTED_OUT_PATH))
        sfout.close()
    json_str = json.dumps(data_to_fix, indent=2)
    with open(OUTPUT_PATH, "w") as fout:
        fout.write(json_str)
        print("File has been saved to the path: {}".format(OUTPUT_PATH))
        fout.close()
        

if __name__=="__main__":
    main()

