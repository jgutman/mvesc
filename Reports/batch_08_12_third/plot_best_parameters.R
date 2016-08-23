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

### Study Model Chosen Parameters ###
# get top 20 logit model parameters
for (top_num in c(20)) {
  top_logit = reports_ref %>% 
    filter(model_name == 'logit', label == 'definite_plus_ogt') %>%
    grab_top_performing('cv_score', top_num, c('prediction_grade')) %>%
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
  ggsave(paste0('best_parameter_of_models/logit_top_', top_num, '.pdf'), g, w = 8, h = 8)
  
  # get top 20 RF model parameters
  top_RF = reports_ref %>% 
    filter(model_name == 'RF', label == 'definite_plus_ogt') %>%
    grab_top_performing('cv_score', top_num, c('prediction_grade')) %>%
    select_('prediction_grade', 'parameters', 'cv_score', 'val_recall_5_15') %>%
    collect()
  # split on parameters for logit
  RF_params = top_RF %>% separate(parameters, sep = ';',
                                  into = c('criterion', 'depth', 'max_features',
                                           'min_samples_split'), extra = 'drop') %>%
    mutate(rank = row_number(desc(cv_score))) %>%
    unite(depth_min_samples, depth, min_samples_split) %>%
    filter(rank <= 10)
  g = ggplot(RF_params, aes(x = rank, y = cv_score, 
                            color = max_features, shape = depth_min_samples)) +
    geom_point(size = 4) + facet_grid(criterion~prediction_grade, scales = 'free_y') +
    ggtitle("RF Best Params on Top 10 for prediction grade
          (Features = all, label = 'definite_plus_ogt')")
  ggsave(paste0('best_parameter_of_models/RF_top_', top_num, '.pdf'), g, w = 11, h = 8)
}