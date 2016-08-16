### Summarizing Third Batch Run 08_12 ###

reports_ref = load_table_ref('~/mvesc/Reports/batch_third_0812/',
                             'custom_precision_5_15',
                             '08_12_2016',
                             where_statement = "where batch_name like '08_12_2016%'")

# further filter reports_ref
reports_ref = reports_ref %>% filter(feature_categories == 
                                       'absence, demographics, grades, intervention, mobility, oaa_normalized, snapshots')

# For Jackie, get the filenames of the top RF models
top1_files = reports_ref %>%
  grab_top_performing('cv_score', 1, vec_to_group_on) %>%
  select_(.dots = c(vec_to_group_on, "filename")) %>%
  filter(model_name %in% c('RF', 'logit')) %>% collect()
top1_files


# Performance of Models Over Time
vec_to_group_on = c('model_name', 'prediction_grade', 'label')
extra_facet_etc_var = c("label")
by_grade_label_top1 <- reports_ref %>% 
  grab_top_performing('cv_score', 1, vec_to_group_on) %>%
  filter(model_name != 'DT')
for (metric in c('precision', 'recall')) {
  plot_obj <- by_grade_label_top1 %>%
    collect_and_ggplot_obj(c(paste0('val_', metric, '_5_15'), 
                             paste0('test_', metric, '_5_15')), 
                           vec_to_group_on,
                           xvar = "prediction_grade",
                           color_var = "model_name",
                           extra_facet_etc_var)
  # plot
  g <- plot_obj + geom_point(size = 4) + facet_wrap(~label) + geom_line() +
    ylab(paste0('avg_', metric, '_5_15')) +
    ggtitle(paste0("Top 1 Model for avg_", metric, "_5_15 by Model Type"))
  ggsave(g, filename = paste0('compare_model_by_prediction_grade_avg_', 
                              metric,'.pdf'), w = 8, h = 8)
}


# Compare the Top 5 Performing Models #
top5_by_model <- reports_ref %>%
  grab_top_performing('cv_score', 5, vec_to_group_on) %>%
  filter(model_name != "DT") %>%
  collect_and_ggplot_obj(c("cv_score"), c(vec_to_group_on, "rank"),
                         xvar = 'rank', color_var = 'model_name',
                         extra_var = c("label"))
g <- top5_by_model + geom_point(size = 4) + 
  facet_wrap(~prediction_grade + label, ncol = 3) +
  ylab('CV_prec_5_15 score') + ggtitle('Top 5 performing by model & grade')
g


### Comparing the downsampling rates ###
# MISSING COLUMN IN DOWNSAMPLING
# downsample_compare <- reports_ref %>%
#   grab_top_performing('val_precision_5_15', 1, 
#                       c(vec_to_group_on, 'downsample')) %>%
#   filter(model_name != 'DT', label == 'definite_plus_ogt') %>%
#   collect_and_ggplot_obj(vec_to_gather = c('val_precision_5_15',
#                                            'test_precision_5_15'),
#                          vec_to_group_on = c('model_name', 'prediction_grade',
#                                              'downsample'),
#                          xvar = 'prediction_grade',
#                          color_var = 'downsample',
#                          extra_var = 'label')

### Comparing Feature Importance ###
feature_compare <- reports_ref %>%
  grab_top_performing('cv_score', 1,
                      c(vec_to_group_on, 'feature_categories')) %>%
  filter(model_name != 'DT', label == 'definite_plus_ogt') %>%
  collect_and_ggplot_obj(vec_to_gather = c('train_precision_5_15'), #'test_precision_5_15'),
                         vec_to_group_on = c('model_name', 'prediction_grade',
                                             'feature_categories'),
                         xvar = 'prediction_grade',
                         color_var = 'feature_categories',
                         extra_var = 'label')
g <- feature_compare + geom_point(size = 4) + facet_wrap(~model_name) + geom_line() +
  ylab(paste0('avg_precision_5_15')) +
  ggtitle(paste0("Top 1 Model for avg_precision_5_15 by Model Type"))


### Study Model Chosen Parameters ###


### Compare Students Across Model Predictions ###


