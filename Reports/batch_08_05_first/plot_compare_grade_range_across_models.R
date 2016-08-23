### Summarizing First Run 08_05 ###

# Get the reference to the `reports` table
#   function automatically gets rid of debug rows
#   and redundant rows with multiple cv_criterion in first batch
#   and automatically loads appropriate packages
#   and allows a custom where statement to get the appropriate batch
reports_ref = load_table_ref('~/mvesc/Reports/batch_08_05_first/',
                             'custom_precision_5',
                             "where batch_name = 'first_run'")


### (3) Compare a small group of models ###
plot_multiple_model_on_grade = function(df, score_col, model_vector,
                                        outcome_label, impute_type,
                                        scale_type) {
  filtered_ref = df %>% filter(label == outcome_label,
                               model_name %in% model_vector,
                               imputation == impute_type,
                               scaling == scale_type,
                               cv_scheme == 'k_fold') %>%
    select_(score_col, "feature_categories", 
            "cv_scheme", "feature_grades", "model_name")
  # get into memory
  plot_df = collect(filtered_ref) %>%
    mutate(feature_name = ifelse(str_count(feature_categories, ",") > 4,
                                 "all_features", feature_categories))
  
  # plot
  #   should have 12 dots for each grade_range
  #   2 impute X 2 scaling X 3 cv
  g <- ggplot(plot_df, aes_string(x = "feature_grades", y = score_col,
                                  color = "feature_name",
                                  group = "feature_name")) +
    geom_point(size = 3, alpha = 1) +
    geom_line() +
    facet_wrap(~model_name) + theme_bw() +
    ggtitle(paste("Grade Ranges: for", 
                  model_vector, "models\nusing label", outcome_label,
                  "\n with cv_scheme k-fold",
                  "\ngiven", impute_type, scale_type))
  g # return
}

# LOOP OVER OUTCOMES #
for (metric in c('val_precision_10')){
  for (outcome in c('not_on_time', 'definite', 'is_dropout')) {
    g = plot_multiple_model_on_grade(reports_ref, metric,
                                     c('logit', 'RF', 'GB', 'SVM'),
                                     outcome, 'median_plus_dummies',
                                     'robust')
    ggsave(plot = g, 
           filename = paste0('compare_across_models/lr_rf_gb_svm_',
                             metric, '_', outcome, '.pdf'),
           w = 8, h = 8)
  }
}