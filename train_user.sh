python train_user.py \
    --model_name_or_path model_for_user_train/per_best_model0001 \
    --output_dir ./user-ner \
    --do_train True \
    --do_eval True \
    --overwrite_output_dir True \
    --use_augmented_data False \
    --train_file ./data_user/train0000.json \
    --validation_file ./data_user/valid0000.json \
    --num_train_epochs 6 \
    --logging_first_step True \
    --logging_steps 200 \
    --eval_steps 200 \
    --evaluation_strategy "steps" \
    --per_device_train_batch_size 2 \
    --fp16_full_eval True \
    --return_entity_level_metrics True \
    --learning_rate 0.000003 \
    --label_all_tokens True \
    --ignore_mismatched_sizes True \
    --use_padding_for_context True \
    --fp16 True \
    --fp16_opt_level O1 \
    --write_badcases True \
    --badcases_dir ./badcases_train \
    --lr_scheduler_type cosine \
    --warmup_ratio 0.20 \
    --input_window_size 8 \
    --draw_curve_or_not True \
    --curve_save_dir ./curves_train \
    --gradient_accumulation_steps 2 \
    --save_curve_step 200 \
    --save_strategy "steps" \
    --save_steps 800000 \
    --best_model_dir ./best_model_user \
    --save_my_best_model_or_not True \
    --best_metrics_keys_list "PR_auc,ROC_auc" \
    --max_seq_length 150 \
    --use_special_tokens_or_not False \
    --special_tokens_list "[USER],[ADVISOR]" \
