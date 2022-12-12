python modify_data.py \
    --mode split_raw_data \
    --input_file data/big_raw/order.txt \
    --output_file data/big_json/train.json \
    --file_to_be_tagged data/small_json/order.sample.json \
    --raw_data_path data/raw_data/raw_data0000.json \
    --splitted_train_data_path data/train_data/train_data0000.json \
    --splitted_valid_data_path data/valid_data/valid_data0000.json \
    --train_valid_ratio 0.1 \


