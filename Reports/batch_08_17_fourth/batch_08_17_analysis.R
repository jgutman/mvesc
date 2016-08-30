### Summarizing Fourth Batch Run 08_17 ###

reports_ref = load_table_ref('~/mvesc/Reports/batch_08_17_fourth/',
                             'custom_precision_5_15',
                             where_statement = "where batch_name like '08_17_2016%'")

#### UNFINISHED ####
# goal: to plot the full prec and recall curves for each model
#   on the training, test, and validation sets
#   by moving down the list one student at a time

# ## Get the full recall and prec curves
# top_rf_logit = reports_ref %>%
#   filter(model_name %in% c('RF', 'logit'),
#          label == 'definite_plus_ogt') %>%
#   grab_top_performing('cv_score', 1, c('model_name',
#                                        'prediction_grade')) %>% 
#   select(filename, model_name) %>%
#   collect()
# 
# each_pred_list = list()
# for (row in 1:nrow(top_rf_logit)){
#   pred_file = tbl(pg_db, dplyr::sql('SELECT * FROM model.predictions')) %>%
#     filter(filename == top_rf_logit$filename[row]) %>% 
#     select(-one_of("predicted_label", "filename")) %>% collect()
#   # add model_name and pred_grade
#   pred_file$prediction_grade = top_rf_logit$prediction_grade[row]
#   pred_file$model_name = top_rf_logit$model_name[row]
#   # store in the list
#   each_pred_list[[row]] = pred_file
# }
# combined_preds <- ldply(each_pred_list)
# 
# # get rid of student_lookups that do not appear in the comparison years
# only_overlap = combined_preds %>% arrange(student_lookup) %>% 
#   filter(model_name == 'RF') %>%
#   select(student_lookup, prediction_grade, predicted_score) %>% 
#   spread(prediction_grade, predicted_score, fill = NA)
# print(dim(only_overlap))
# only_overlap_lookups = only_overlap %>% drop_na() %>% select(student_lookup)
# print(dim(only_overlap_lookups))
# 
# combined_overlap_only = left_join(only_overlap_lookups,
#                                   combined_preds,
#                                   by = "student_lookup")

