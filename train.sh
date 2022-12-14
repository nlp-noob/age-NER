python train.py \
    --model_name_or_path Jean-Baptiste/camembert-ner-with-dates \
    --output_dir ./test-ner \
    --do_train True \
    --do_eval True \
    --overwrite_output_dir True \
    --use_augmented_data True \
    --train_file ./data/train_data/augmented_win4_dens0_train_data0000.json \
    --validation_file ./data/valid_data/valid_data0000.json \
    --num_train_epochs 5 \
    --logging_first_step True \
    --logging_steps 200 \
    --eval_steps 200 \
    --evaluation_strategy "steps" \
    --per_device_train_batch_size 2 \
    --fp16_full_eval True \
    --return_entity_level_metrics True \
    --learning_rate 0.0000003 \
    --label_all_tokens True \
    --ignore_mismatched_sizes True \
    --use_padding_for_context True \
    --fp16 True \
    --fp16_opt_level O1 \
    --write_badcases True \
    --badcases_dir ./badcases_train \
    --lr_scheduler_type cosine \
    --warmup_ratio 0.20 \
    --input_window_size 4 \
    --draw_curve_or_not True \
    --curve_save_dir ./curves_train \
    --gradient_accumulation_steps 2 \
    --save_curve_step 200 \
    --save_strategy "steps" \
    --save_steps 800000 \
    --best_model_dir ./best_model \
    --save_my_best_model_or_not True \
    --best_metrics_keys_list "PR_auc,ROC_auc,token_level_DATE_f1,token_level_DATE_recall,token_level_DATE_precision" \
    --max_seq_length 150 \
    --use_special_tokens_or_not False \
    --special_tokens_list "[USER],[ADVISOR]" \
    
