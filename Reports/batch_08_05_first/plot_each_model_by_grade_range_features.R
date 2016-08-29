### Summarizing First Run 08_05 ###

# Get the reference to the `reports` table
#   function automatically gets rid of debug rows
#   and redundant rows with multiple cv_criterion in first batch
#   and automatically loads appropriate packages
#   and allows a custom where statement to get the appropriate batch
reports_ref = load_table_ref('~/mvesc/Reports/batch_08_05_first/',
                             'custom_precision_5',
                             "where batch_name = 'first_run'")

### (2) For each specific model, plot how grade range influences ###
#   facet ON feature_category
#   color ON cv_scheme
#   ignore: impute, scaling
plot_each_model_on_grade = function(df, score_col, model_type,
                                      outcome_label) {
  filtered_ref = df %>% filter(label == outcome_label,
                               model_name == model_type,
                               cv_scheme == 'k_fold') %>%
    select_(score_col, "feature_categories", 
            "cv_scheme", "feature_grades", "imputation",
            "scaling")
  # get into memory
  plot_df = collect(filtered_ref) %>%
    mutate(feature_name = ifelse(str_count(feature_categories, ",") > 4,
                                 "all_features", feature_categories)) %>%
    unite(imp_scal, c(imputation, scaling))
  
  # plot
  #   should have 12 dots for each grade_range
  #   2 impute X 2 scaling X 3 cv
  g <- ggplot(plot_df, aes_string(x = "feature_grades", y = score_col,
                            color = "imp_scal")) +
    geom_point(size = 2.5, alpha = 0.75, position = position_jitter(height = 0)) +
    facet_wrap(~feature_categories) + theme_bw() +
    ggtitle(paste("Grade Ranges: for", 
            model_type, "model using label", outcome_label,
            "\n with cv_scheme = k_fold",
            "\n impute/scale in color"))
  g # return
}

# LOOP OVER EACH MODEL TYPE & OUTCOME #
all_models = reports_ref %>% select(model_name) %>% collect() %>% distinct()
for (specific_model in all_models$model_name) {
  for (metric in c('val_precision_10')){
    for (outcome in c('not_on_time', 'definite', 'is_dropout')) {
      g = plot_each_model_on_grade(reports_ref, metric, specific_model, outcome)
      
      ggsave(plot = g, 
             filename = paste0('each_model_by_grade_range_features/',
                               specific_model, '_', metric, '_', outcome,
                               '.pdf'),
             w = 8, h = 8)
    }
  }
}