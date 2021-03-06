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
# further filter reports_ref to focus on only models using
#   only full features
reports_ref = reports_ref %>% filter(feature_categories == 
                                       'absence, demographics, grades, intervention, mobility, oaa_normalized, snapshots')

# Performance of Models Over Time
vec_to_group_on = c('model_name', 'prediction_grade', 'label')
by_grade_label_top1 <- reports_ref %>% 
  grab_top_performing('cv_score', 1, vec_to_group_on) %>%
  filter(model_name != 'DT')
for (metric in c('precision', 'recall')) {
  # optionally, also include test set
  plot_obj <- by_grade_label_top1 %>%
    collect_and_ggplot_obj(c(paste0('val_', metric, '_5_15')), 
#                             paste0('test_', metric, '_5_15')), 
                           vec_to_group_on,
                           xvar = "prediction_grade",
                           color_var = "model_name")
  # plot
  g <- plot_obj + geom_point(size = 4) + facet_wrap(~label, scales = 'free_y') + geom_line() +
    ylab(paste0('avg_', metric, '_5_15')) +
    ggtitle(paste0("Top 1 Model for avg_", metric, "_5_15 by Model Type"))
  ggsave(g, filename = paste0('compare_model_over_prediction_grade/all_outcomes_of_',
                              metric,'_top1.pdf'), w = 8, h = 8)
}