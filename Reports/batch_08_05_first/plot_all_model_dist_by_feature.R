### Summarizing First Run 08_05 ###

# Get the reference to the `reports` table
#   function automatically gets rid of debug rows
#   and redundant rows with multiple cv_criterion in first batch
#   and automatically loads appropriate packages
#   and allows a custom where statement to get the appropriate batch
reports_ref = load_table_ref('~/mvesc/Reports/batch_08_05_first/',
                             'custom_precision_5',
                             "where batch_name = 'first_run'")

### (1) Plot the Overall Distribution for each Model Name ###
#   dot plot of all the runs for each model
#   group by model type and get the top performances in a certain category

for (metric in c('val_precision_10')){
  for (outcome in c('not_on_time', 'definite', 'is_dropout')) {
    for (top_num in c(12, 99)) {
    # identify vec_to_group_on
    vec_to_group_on = c('model_name', 'label', 'feature_categories')
    top_performing_ref = grab_top_performing(reports_ref, score_col = metric,
                                             top_num = top_num,
                                             vec_to_group_on)
    # keep only specific label
    label_top_ref = top_performing_ref %>% filter(label == outcome)
    # get ggplot object
    plot_obj = collect_and_ggplot_obj(label_top_ref, 
                                      vec_to_gather = metric,
                                      c(vec_to_group_on, 'rank'),
                                      xvar = 'model_name',
                                      color_var = 'feature_categories')
    
    # adjust the plot_obj data to revise the feature labels
    plot_obj$data = plot_obj$data %>%
      mutate(feature_categories = 
               ifelse(str_count(feature_categories, ",") > 4,
                      "full_features", feature_categories))
    # refactor based on best "full_features"
    ordering_models = plot_obj$data %>% filter(feature_categories == 'full_features') %>%
      arrange(desc(avg_metric)) %>% distinct(model_name)
    # refactor plot_obj model_names based on this
    plot_obj$data = plot_obj$data %>% ungroup() %>%
      mutate(model_name = factor(model_name, levels = ordering_models$model_name))
    
    # create the plot layers
    g = plot_obj + geom_point(position = position_jitter(h = 0)) + 
      ylab('Val Prec 10') + xlab("Model Family (default param)") +
      ggtitle(paste("All Runs", metric, "keep only top", top_num,
                    "of each feature;\nuse label", outcome,
                    "\nignoring grade_range, impute, scaling, cv_scheme info"))
    ggsave(plot = g,
           filename = paste0('all_model_dist/dist_', metric,
                             '_', outcome, '_top', top_num, '.pdf'),
           w = 11, h = 8)
    
    # if top 12, also created a summarized average
    if (top_num == 12) {
      plot_obj$data = plot_obj$data %>% group_by(model_name, feature_categories) %>%
        summarise(avg_metric = mean(avg_metric))
      summarized_g = plot_obj + geom_point(size = 4) + geom_line() + 
        ylab('Val Prec 10') + xlab("Model Family (default param)") +
        ggtitle(paste("All Runs", metric, "of avg top", top_num,
                      "of each feature;\nuse label", outcome,
                      "\nignoring grade_range, impute, scaling, cv_scheme info"))
      ggsave(plot = g,
             filename = paste0('all_model_dist/avgd_dist_', metric,
                               '_', outcome, '_top', top_num, '.pdf'),
             w = 11, h = 8)
    }
    }
  }
}