### Summarizing Third Batch Run 08_12 ###

reports_ref = load_table_ref('~/mvesc/Reports/batch_08_17_2016/',
                             'custom_precision_5_15',
                             where_statement = "where batch_name like '08_17_2016%'")

# For Jackie, get the filenames of the top RF models
# output CSV of the filenames for the top 30 performing models for each
#   prediction_grade
#   label
#   feature_categories
#   model_name
#   ranked by
#     val_recall_5_15
group_to_keep = c('model_name', 'prediction_grade',
                  'label', 'feature_categories')
top20_files = reports_ref %>%
  grab_top_performing('cv_score', 20, group_to_keep) %>%
  select_(.dots = c(group_to_keep, "filename")) %>%
  collect()
write.csv(top20_files, file = 'top20_by_cv_score_on_pred_grade_label_model_features.csv')


# Performance of Models Over Time
vec_to_group_on = c('model_name', 'prediction_grade', 'label')
extra_facet_etc_var = c("label")
by_grade_label_top1 <- reports_ref %>% 
  grab_top_performing('cv_score', 1, vec_to_group_on) %>%
  filter(model_name != 'DT')
for (metric in c('precision', 'recall')) {
  plot_obj <- by_grade_label_top1 %>%
    collect_and_ggplot_obj(c(paste0('val_', metric, '_5_15')), 
                           vec_to_group_on,
                           xvar = "prediction_grade",
                           color_var = "model_name",
                           extra_facet_etc_var)
  # plot
  g <- plot_obj + geom_point(size = 4) + facet_wrap(~label, scales = 'free_y') + geom_line() +
    ylab(paste0('avg_', metric, '_5_15')) +
    ggtitle(paste0("Top 1 Model for val_", metric, "_5_15 by Model Type"))
  ggsave(g, filename = paste0('compare_model_by_prediction_grade_val_', 
                              metric,'.pdf'), w = 8, h = 8)
}


## Get the full recall and prec curves
top_rf_logit = reports_ref %>%
  filter(model_name %in% c('RF', 'logit'),
         label == 'definite_plus_ogt') %>%
  grab_top_performing('cv_score', 1, c('model_name',
                                       'prediction_grade')) %>% 
  select(filename, model_name) %>%
  collect()

each_pred_list = list()
for (row in 1:nrow(top_rf_logit)){
  pred_file = tbl(pg_db, dplyr::sql('SELECT * FROM model.predictions_new')) %>%
    filter(filename == top_rf_logit$filename[row]) %>% 
    select(-one_of("predicted_label", "filename")) %>% collect()
  # add model_name and pred_grade
  pred_file$prediction_grade = top_rf_logit$prediction_grade[row]
  pred_file$model_name = top_rf_logit$model_name[row]
  # store in the list
  each_pred_list[[row]] = pred_file
}
combined_preds <- ldply(each_pred_list)
saveRDS(combined_preds, file = 'top1_each_grade_rf_logit.rds')

# get rid of student_
only_overlap = combined_preds %>% arrange(student_lookup) %>% 
  filter(model_name == 'RF') %>%
  select(student_lookup, prediction_grade, predicted_score) %>% 
  spread(prediction_grade, predicted_score, fill = NA)
print(dim(only_overlap))
only_overlap_lookups = only_overlap %>% drop_na() %>% select(student_lookup)
print(dim(only_overlap_lookups))

combined_overlap_only = left_join(only_overlap_lookups,
                                  combined_preds,
                                  by = "student_lookup")

# plot density for our top models

# plot rank comparisons for our top models

# plot recall curves for our top models


### Study Model Chosen Parameters ###
# get top 30 logit model parameters
top_logit = reports_ref %>% 
  filter(model_name == 'logit', label == 'definite_plus_ogt') %>%
  grab_top_performing('cv_score', 20, c('prediction_grade')) %>%
  select_('prediction_grade', 'parameters', 'cv_score', 'val_recall_5_15') %>%
  collect()
# split on parameters for logit
logit_params = top_logit %>% separate(parameters, sep = ';',
                                      into = c('C', 'penalty')) %>%
  mutate(rank = row_number(desc(cv_score)))
g = ggplot(logit_params, aes(x = rank, y = cv_score, 
                             color = C, shape = penalty)) +
  geom_point(size = 4) + facet_wrap(~prediction_grade, scales = 'free_y') +
  ggtitle("Logit Best Params on Top 20 for prediction grade
          (Features = all, label = 'definite_plus_ogt')")


### OLD ###

ranked_pred_by_model = combined_pred %>% group_by(model_name) %>% mutate(rank = row_number(predicted_score)) %>%
  ggplot(aes(x = rank, y = predicted_score, color = model_name)) + geom_point()

by_id_diff = combined_pred %>% group_by(model_name, split) %>%
  select(-one_of('filename', 'predicted_label')) %>%
  spread(model_name, predicted_score) %>%
  mutate(rf_diff_lr = RF - logit,
         rf_rank = row_number(desc(RF)),
         lr_rank = row_number(desc(logit)),
         rank_diff = rf_rank - lr_rank,
         diff_order = row_number(desc(rf_diff_lr)),
         rank_diff_order = row_number(desc(rank_diff)))
# plot based on actual diff
ggplot(by_id_diff, aes(x = diff_order, y = rf_diff_lr, color = factor(true_label))) + 
  geom_point(position = position_dodge(width = 0.5)) +
  facet_wrap(~split)
# based on rank diff
ggplot(by_id_diff, aes(x = rank_diff_order, y = rank_diff, color = factor(true_label))) + 
  geom_point(position = position_jitter(width = 10, h = 10)) +
  facet_wrap(~split) + ggtitle("RF Rank - Logit Rank (neg = RF puts more risky)")

# scatter diff versus logit predictions
ggplot(by_id_diff, aes(x = lr_rank, y = rank_diff, color = factor(true_label))) +
  geom_point() + geom_smooth() +
  facet_wrap(~split) + ggtitle("RF Rank - Logit Rank (neg = RF puts more risky)
                               scattered on logit rank on x-axis")

ggplot(by_id_diff, aes(x = rf_rank, y = rank_diff, color = factor(true_label))) + 
  geom_point() + geom_smooth() +
  facet_wrap(~split) + ggtitle("RF Rank - Logit Rank (neg = RF puts more risky)
                               scattered on rf rank on x-axis")

g <- ggplot(filter(by_id_diff, true_label != 0), aes(x = lr_rank, y = rf_rank, color = factor(true_label))) + 
  geom_point() + geom_smooth() + geom_abline(slope = 1, intercept = 0) +
  facet_wrap(~split) + ggtitle("RF Rank vs Logit Rank") + theme_bw()
g
ggsave(g, filename = 'rank_comparison_top_rf_logit.pdf', w = 8, h = 8)

# by actual probability pred
g <- ggplot(filter(by_id_diff, true_label == 1), aes(x = logit, y = RF, color = factor(true_label))) + 
  geom_point() + geom_smooth() + geom_abline(slope = 1, intercept = 0) +
  facet_wrap(~split) + ggtitle("RF Prob vs Logit Prob") + theme_bw()
g

# density plot of probabilities
with_cutoff_line = combined_pred %>% group_by(model_name, split) %>%
  mutate(rank = row_number(desc(predicted_score)),
         cutoff = rank <= n() * 0.10) %>%
  group_by(model_name, split, cutoff) %>%
  mutate(cutoff_val = last(predicted_score, order_by = rank))

ggplot(combined_pred, aes(x = predicted_score, fill = factor(true_label),
                          color = factor(true_label))) + 
  facet_grid(model_name~split) +
  geom_freqpoly() + ylim(0, 50)
