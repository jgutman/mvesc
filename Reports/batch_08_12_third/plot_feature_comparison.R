### Summarizing Third Batch Run 08_12 ###

# Get the reference to the `reports` table
#   sets the correct working directory to make reports
#   function automatically gets rid of debug rows
#   and redundant rows with multiple cv_criterion in first batch
#   and automatically loads appropriate packages
#   and allows a custom where statement to get the appropriate batch
reports_ref = load_table_ref('~/mvesc/Reports/batch_08_12_third/',
                             'custom_precision_5_15',
                             "where batch_name like '08_12_2016_%'")

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
ggsave(plot = g, filename = 'compare_feature_sets_by_prediction_grade.pdf', w = 8, h = 8)
