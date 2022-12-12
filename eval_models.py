from transformers import HfArgumentParser
from transformers import Trainer
from transformers import DataCollatorForTokenClassification
import datasets
import numpy as np
import torch
import logging

from transformers import AutoTokenizer, AutoModelForTokenClassification
from typing import Dict, List, Optional, Union, Any
import json
import evaluate
from dataclasses import dataclass, field

# mymodule
from train import CustomTrainer
from train import get_my_dataset
from utils.order_extract import extract_data
from utils.tag_manually import terminal_tagging
from conf.evaluation_conf import MODEL_LIST, MANNUAL_METHOD

tokenizer = None
column_names = None




@dataclass
class CustomArguments:
    """
    Arguments for how to modifiy the data.
    """
    mode: str = field(
        metadata={"help": (
                "you should specify the mode you wanna use with this module."
                "choose from below:"
                "{eval_model_in_list} : eval the models in the list."
                "{eval_by_method} : eval bfy the method which is set mannually."
                "{eval_saved_model} : eval-the model in the folder that saved before"
                )
        },
    )
    input_window_size: int = field(
        metadata={"help": (
                "the windowsize above the user sentence."
                )
        },
    )
    data_path: str = field(
        metadata={"help": (
                "the data file for eval."
                )
        },
    )

def eval_model(model_path, data_path, window_size):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    data_collator = DataCollatorForTokenClassification(tokenizer)
    model = AutoModelForTokenClassification.from_pretrained(model_path)
    model.to(torch.device("cuda"))
    dataset_dict = {}
    label_list = list(model.config.label2id.keys())
    have_pre = False
    for a_label in label_list:
        if a_label == "B-DATE":
            have_pre = True
    dataset_dict["validation"] = get_my_dataset(data_path, window_size, have_pre=have_pre) 
    raw_datasets = datasets.DatasetDict(dataset_dict) 
    column_names = raw_datasets["validation"].column_names
    eval_dataset = raw_datasets["validation"]

    def tokenize_and_align_labels(examples):
        # check for bottom line
        text_column_name = "tokens"
        label_column_name = "ner_tags"
        for i, tokens_check in enumerate(examples[text_column_name]):
            bottom_len = examples["bottom_len"][i]
            if examples["tokens"][i][-bottom_len]!="[USER]":
                raise ValueError("wrong dataset")
            
        tokenized_inputs = tokenizer(
            examples[text_column_name],
            truncation=True,
            # We use this argument because the texts in our dataset are lists of words (with a label for each word).
            is_split_into_words=True,
        )
        labels = []
        for i, label in enumerate(examples[label_column_name]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            previous_word_idx = None
            label_ids = []

            for j, word_idx in enumerate(word_ids):
                # Special tokens have a word id that is None. We set the label to -100 so they are automatically
                # ignored in the loss function.
                if word_idx is None:
                    label_ids.append(-100)
                # We set the label for the first token of each word.
                elif word_idx != previous_word_idx:
                    label_ids.append(model.config.label2id[label[word_idx]])
                # For the other tokens in a word, we set the label to either the current label or -100, depending on
                # the label_all_tokens flag.
                else:
                    label_ids.append(model.config.label2id[label[word_idx]])
                previous_word_idx = word_idx
            labels.append(label_ids)
        tokenized_inputs["labels"] = labels
        return tokenized_inputs
    eval_dataset = eval_dataset.map(
        tokenize_and_align_labels,
        batched=True,
    )

    def _split_into_word_list(labels):
        flattened_labels = []
        for a_line_labels in labels:
            for a_label in a_line_labels:
                # 因为这个是模型的预测结果，不会再进行id映射，定义一个任意的label告诉metrics这是单独的片段即可
                if a_label!="O":
                    a_label="B-DATE"
                flattened_labels.append([a_label])
        return flattened_labels

    def compute_metrics(p):
        metric = evaluate.load("seqeval")
        #########
        predictions = p.predictions
        labels = p.label_ids
        #########
        # predictions, labels = p
        predictions = np.argmax(predictions, axis=2)
    
        # Remove ignored index (special tokens)
        true_predictions = [
            [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
    
    
        true_pred_splitted = _split_into_word_list(true_predictions)
        true_labels_splitted = _split_into_word_list(true_labels)
    
        # 按照词片段
        results_piece = metric.compute(predictions=true_predictions, references=true_labels)
        # 按照标签
        results_token_level = metric.compute(predictions=true_pred_splitted, references=true_labels_splitted)
        # Unpack nested dictionaries
        final_results = {}
        for key, value in results_piece.items():
            if isinstance(value, dict):
                for n, v in value.items():
                    final_results[f"word_piece_{key}_{n}"] = v
            else:
                final_results["word_piece_" + key] = value
        for key, value in results_token_level.items():
            if isinstance(value, dict):
                for n, v in value.items():
                    final_results[f"token_level_{key}_{n}"] = v
            else:
                final_results["token_level_" + key] = value
        return final_results

    trainer = CustomTrainer(
        model=model,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    metrics = trainer.evaluate()
    print(metrics)


def main():


    mode_list = ["eval_model_in_list", "eval_by_method"]
    parser = HfArgumentParser((CustomArguments))
    custom_args = parser.parse_args_into_dataclasses()[0]
    if custom_args.mode == "eval_model_in_list":
        print("**"*30)
        print("0 : {eval_all_model_bellow}")
        for model_num, model_path in enumerate(MODEL_LIST):
            print(str(model_num+1)+"\t:\t"+model_path)
        print("**"*30)
        while(True):
            user_choice = input("please choose the model ot eval:\t")
            user_choice = int(user_choice)
            break
        if user_choice == 0:
            for model_path in MODEL_LIST:
                pass
        else:
            model_path = MODEL_LIST[user_choice-1]
            print("you chose the model: {}".format(model_path))
            eval_model(model_path, custom_args.data_path, custom_args.input_window_size)
            

    elif custom_args.mode == "eval_by_method":
        print("**"*30)
        print("0 : {eval_all_model_bellow}")
        for model_num, model_path in enumerate(MANNUAL_METHOD):
            print(model_num+1+"\t:\t"+model_path)
        print("**"*30)
        while(True):
            user_choice = input("please choose the model ot eval")
            user_choice = int(user_choice)
        


if __name__=="__main__":
    main()

