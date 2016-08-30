### Summarizing Second Run 08_09 ###

# Get the reference to the `reports` table
#   function automatically gets rid of debug rows
#   and redundant rows with multiple cv_criterion in first batch
#   and automatically loads appropriate packages
#   and allows a custom where statement to get the appropriate batch
reports_ref = load_table_ref('~/mvesc/Reports/batch_08_09_second/',
                             'custom_precision_10',
                             "where batch_name like '08_09_2016_%'")

# evaluate cv_scheme over top N models

for (outcome in c('definite', 'not_on_time', 'is_dropout')) {
  for (top_num in c(5, 1)){
    # can ONLY look at grades 7 and 8 here because
    #   models did not finish running for grades 9 and 10 in batch two
    g = compare_cv_scheme(reports_ref, score_col = 'cv_score',
                          outcome = outcome,
                          top_num = top_num,
                          vec_to_group_on = c("model_name", "cv_scheme", "prediction_grade", "label"),
                          vec_to_gather = c('val_recall_3', 'val_recall_5', 'val_recall_10'),
                          filter_grade_levels = c(7, 8))
    g = g + ylab('Val Recall Over K') + xlab('K% of Students') + 
      ggtitle('Validation Recall Performance colored by cv_scheme')
    ggsave(plot = g, 
           filename = paste0('compare_cv_scheme/outcome_', outcome, 
                             '_avgd_over_top_', top_num, '.pdf'),
           w = 10, h = 8)
  }
}

# (2) Evaluate model performance overall by Prediction Grade #
for (outcome in c('definite', 'not_on_time', 'is_dropout')) {
  for (top_num in c(1)){
    vec_to_group_on = c("model_name", "prediction_grade", "label")
    vec_to_gather = c('val_recall_3', 'val_recall_5', 'val_recall_10')
    top_ref = grab_top_performing(reports_ref, "cv_score", 
                                  top_num = 1, 
                                  vec_to_group_on) %>%
      filter(label == outcome)
    # get plot obj
    plot_obj = collect_and_ggplot_obj(top_ref, vec_to_gather,
                                      c(vec_to_group_on, "k_pcnt_intervene"),
                                      xvar = "k_pcnt_intervene",
                                      color_var = "model_name") 
    plot_obj$data = plot_obj$data %>%
      mutate(k_pcnt_intervene = as.numeric(as.character(k_pcnt_intervene)),
             prediction_grade = factor(prediction_grade))
    # plot
    g = plot_obj + geom_point(size = 3) + geom_line() +
      facet_wrap(~prediction_grade, nrow = 1)
    # save
    ggsave(plot = g, 
           filename = paste0('overall_model_performance/outcome_', outcome, 
                             '_avgd_over_top_', top_num, '.pdf'),
           w = 10, h = 8)
  }
}


##################
#### UNUSED ######
##################
# 
# ### MISC: Run Time ###
# # avg run time by model type
# avg_run_time = batch_two %>% filter(label == "not_on_time") %>% group_by(model_name) %>% 
#   summarise(mean_time = mean(time)) %>% collect()
# print(avg_run_time, n = 10)
# 
# # avg run time of GB by parameters
# avg_GB_time = batch_two %>% filter(label == "not_on_time",
#                                     model_name == 'GB') %>%
#   group_by(parameters) %>% 
#   summarise(mean_time = mean(time)) %>% 
#   arrange(desc(mean_time)) %>% collect()
# print.data.frame(avg_GB_time)
# 
# 
# ### UNFINISHED: Compare Given Model to Its Parameters ###
# look_at_one_model_parameters = function(ref, model) {
#   model_ref = ref %>% filter(model_name == model,
#                              label == 'not_on_time') %>%
#     select(model_name, parameters, prediction_grade, cv_score, 
#            val_recall_3, val_recall_5, val_recall_10,
#            test_recall_3, test_recall_5, test_recall_10)
#   
#   df = collect(model_ref) 
#   
#   gathered = gather_recall_3_10(df, c("model_name", "prediction_grade", 
#                                       "metric_type", "k_pcnt_intervene",
#                                       "parameters"))
#   
#   plot_df = gathered %>% separate(parameters,
#                             into = paste0("p", seq(4)),
#                             sep = "; ", extra = 'merge') %>%
#     unite(p1p2, p1, p2, remove = F)
#   
#   
#   # ggplot by prediction_grade
#   g <- ggplot(filter(plot_df, prediction_grade == 6), 
#               aes(x = k_pcnt_intervene,
#                            y = avg_recall,
#                            color = p1,
#                            group = p1p2,
#                            linetype = p2))
#   
#   g + geom_point() + facet_grid(p3~p4) + geom_line() + ggtitle(paste(model, "parameters"))
#   
#   ## or
#   g <- ggplot(filter(gathered, prediction_grade == 6),
#               aes(x = k_pcnt_intervene, y = avg_recall, 
#                   color = parameters, group = parameters))
#   g + geom_point() + geom_line() + theme(legend.position="none")
# }