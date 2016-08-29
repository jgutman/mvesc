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


### Compare the Top 5 Performing Models ###
top5_by_model <- reports_ref %>%
  grab_top_performing('cv_score', 5, vec_to_group_on) %>%
  filter(model_name != "DT") %>%
  collect_and_ggplot_obj(c("cv_score"), c(vec_to_group_on, "rank"),
                         xvar = 'rank', color_var = 'model_name')
g <- top5_by_model + geom_point(size = 4) + 
  facet_wrap(~prediction_grade + label, ncol = 3) +
  ylab('CV_prec_5_15 score') + ggtitle('Top 5 performing by model & grade')
ggsave(plot = g, filename = 'top5_performing_cv_scores_by_outcome_model.pdf', w = 10, h = 10)
