python modify_data.py \
    --mode split_tagged_data_to_train_valid \
    --input_file data/user_index_data/tagged_raw_date_data.json \
    --output_file data/large_json/empty.json \
    --file_to_be_tagged data/large_json/empty.json \
    --raw_data_path data/raw_data/raw_data0000.json \
    --splitted_train_data_path data_user/train0000.json \
    --splitted_valid_data_path data_user/valid0000.json \
    --train_valid_ratio 0.1 \
    --user_template_path tag_user_template.json \

