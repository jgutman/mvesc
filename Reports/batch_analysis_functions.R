# graphing functions for batch run analysis

load_table_ref = function(wd_loc, criterion_name,
                          where_statement = '',
                          table_name = 'model.reports'){
  # Load required credentials and libraries
  library("plyr"); library("dplyr"); library("ggplot2");
  library("tidyr"); library("stringr"); library("RPostgreSQL")
  library("lazyeval"); library("lubridate")
  
  # getting postgres database credentials
  pgpass = str_split(read.table("/mnt/data/mvesc/pgpass")[1,1], ":")[[1]]
  # connecting to db
  pg_db = src_postgres(dbname = pgpass[3], host = pgpass[1],
                       port = pgpass[2], user = pgpass[4], password = pgpass[5])
  
  # also set wd for saving
  setwd(wd_loc)
  
  # Get the reference to the `reports` table
  reports_ref = tbl(pg_db, dplyr::sql(paste('SELECT * FROM', table_name,
                                            sql(where_statement))))
  
  filtered_reports_ref = reports_ref %>%
    filter(cv_criterion == criterion_name,
           debug == FALSE)
  return(filtered_reports_ref)
}

grab_top_performing = function(ref, score_col, top_num,
                               vec_to_group_on) {
  # Searches the database (based on pre-exisitng filters in ref)
  #   and returns a SQL reference with just the top_num within the group
  # score_col = criteria to rank on
  # top_num = number of top ones to keep
  # vec_to_group_on = character vector of columns to group on
  
  top_dat = ref %>% group_by_(.dots = vec_to_group_on) %>%
    mutate_(rank = interp(~row_number(desc(v)), v = as.name(score_col))) %>%
    filter(rank <= top_num)
  
  # return
  top_dat
}

gather_multiple_criteria = function(df, vec_to_gather, vec_to_group_on){
  # Takes in a data.frame (already collected from database)
  #  and returns a longer dataframe of several metrics
  # Allows for easy averaging of performance on val & test sets
  # vec_to_gather: a vector of column names to gather on
  # vec_to_group_on: a vector to keep (group on) during the gather
  
  df %>% ungroup() %>% gather_("metric_k", "score", vec_to_gather) %>%
    separate(metric_k, c("dataset", "metric_type", "k_pcnt_intervene"), 
             sep = "_", extra = 'merge') %>%
    group_by_(.dots = vec_to_group_on) %>% 
    summarise(avg_metric = mean(score)) %>% # e.g. avg over the val and test sets
    ungroup()
}

collect_and_ggplot_obj = function(ref, vec_to_gather, vec_to_group_on,
                                  xvar, color_var, extra_var = NA) {
  # identify columns to select
  dots = c(vec_to_gather, vec_to_group_on, xvar, color_var, extra_var)  
  # keep only those that are in the dataset
  dots = intersect(dots, colnames(ref))
  
  # Takes in a db reference and collects a subset of columns to group on
  collected = ref %>% select_(.dots = dots) %>%
    collect() %>% ungroup()
  
  # gather this table and summarize on the vec_to_gather
  # EDGE: Even if there is only one variable to gather, this will still work
  #   though it only keeps the variables chosen to group on
  gathered = gather_multiple_criteria(collected, vec_to_gather,
                                      vec_to_group_on)
  
  # returns ggplot object without geoms
  g <- ggplot(gathered, aes_string(x = xvar, y = "avg_metric",
                                    color = color_var,
                                    group = color_var))
  g
}

## Compare Models on CV_Scheme ##
compare_cv_scheme = function(ref, 
                             score_col = 'cv_score',
                             top_num = 5,
                             outcome = 'definite',
                             vec_to_group_on = c("model_name", "cv_scheme", "prediction_grade", "label"),
                             vec_to_gather = c('val_recall_3', 'val_recall_5', 'val_recall_10'),
                             filter_grade_levels = seq(6, 10),
                             color_var = 'model_name'){
  # grab top model names and cv_scheme
  top_ref = grab_top_performing(ref, score_col, top_num, vec_to_group_on) %>%
    filter(label == outcome)
  
  # collect and gather and return plot obj
  plot_obj = collect_and_ggplot_obj(top_ref, vec_to_gather, 
                                    c(vec_to_group_on, 'k_pcnt_intervene'),
                                    xvar = 'k_pcnt_intervene',
                                    color_var = color_var)
  
  # focus ONLY on grades 7 and 8 because grades 9 & 10 did not finish
  #   and grade 6 only uses k-fold
  plot_obj$data = plot_obj$data %>%
    mutate(k_pcnt_intervene = as.numeric(as.character(k_pcnt_intervene)),
           prediction_grade = factor(prediction_grade)) %>%
    filter(prediction_grade %in% filter_grade_levels) %>%
    unite(cv_scheme_time, cv_scheme, prediction_grade, remove = F)
  
  # ggplot by prediction_grade
  g = plot_obj + geom_point() + 
    facet_grid(prediction_grade ~ model_name) + 
    geom_line(aes(group = cv_scheme_time))
  # return
  g
}

## Plot Rank Comparison between RF and logit ###
get_rank_comparison_df = function(ref, outcome, grade, score_col) {
  top_rf_logit = ref %>%
    filter(model_name %in% c('RF', 'logit'),
           prediction_grade == grade,
           label == outcome) %>%
    grab_top_performing(score_col, 1, c('model_name')) %>% collect()
  
  # get predictions for each model
  # getting postgres database credentials
  pgpass = str_split(read.table("/mnt/data/mvesc/pgpass")[1,1], ":")[[1]]
  # connecting to db
  pg_db = src_postgres(dbname = pgpass[3], host = pgpass[1],
                       port = pgpass[2], user = pgpass[4], password = pgpass[5])
  # grab predictions
  predictions_ref = tbl(pg_db, dplyr::sql('SELECT * FROM model.predictions'))
  rf_pred = predictions_ref %>% filter(filename == top_rf_logit$filename[top_rf_logit$model_name == 'RF'][[1]]) %>%
    collect()
  logit_pred = predictions_ref %>% filter(filename == top_rf_logit$filename[top_rf_logit$model_name == 'logit'][[1]]) %>%
    collect()
  
  # combine the predictions together for each model
  rf_pred$model_name = 'RF'; logit_pred$model_name = 'logit'
  combined_pred = rbind(rf_pred, logit_pred)
  
  # identify the rank orderings and differences between these two models
  #   group_by model_name and dataset ("split")
  #   and then calculate respective differences
  #   use spread() to make columns for each model
  by_id_diff = combined_pred %>% group_by(model_name, split) %>%
    select(-one_of('filename', 'predicted_label')) %>%
    spread(model_name, predicted_score) %>%
    mutate(rf_diff_lr = RF - logit,
           rf_rank = row_number(desc(RF)),
           lr_rank = row_number(desc(logit)),
           rank_diff = rf_rank - lr_rank,
           diff_order = row_number(desc(rf_diff_lr)),
           rank_diff_order = row_number(desc(rank_diff))) %>%
    # reorder set names
    ungroup() %>%
    mutate(split = factor(split, levels = c('train', 'val', 'test')))
  
  # return
  by_id_diff
}

make_and_save_rank_plots = function(by_id_diff, grade) {
  # make and save the plots
  # BEGIN PLOTS #
  # based on rank diff
  g = ggplot(by_id_diff, aes(x = rank_diff_order, y = rank_diff, color = factor(true_label))) + 
    geom_point(position = position_jitter(width = 10, h = 10)) +
    facet_wrap(~split) + ggtitle("RF Rank - Logit Rank (neg = RF puts more risky)")
  ggsave(paste0('compare_RF_logit_diffs/dist_of_rank_diff_grade', grade, '.pdf'), 
         g, w = 8, h = 8)
  
  # scatter diff versus logit predictions
  g <- ggplot(by_id_diff, aes(x = lr_rank, y = rf_rank, color = factor(true_label))) + 
    geom_point() + geom_smooth() + geom_abline(slope = 1, intercept = 0) +
    facet_wrap(~split) + ggtitle("RF Rank vs Logit Rank") + theme_bw()
  ggsave(paste0('compare_RF_logit_diffs/rank_scatterplot_w_trend_line_grade', grade, '.pdf'),
         g, w = 8, h = 8)
  
  # only with the true labels
  g <- ggplot(filter(by_id_diff, true_label == 1),
              aes(x = lr_rank, y = rf_rank, color = factor(true_label))) + 
    geom_point() + geom_smooth() + geom_abline(slope = 1, intercept = 0) +
    facet_wrap(~split) + ggtitle("RF Rank vs Logit Rank (only ground truth labels)") + theme_bw()
  ggsave(paste0('compare_RF_logit_diffs/rank_scatterplot_w_trend_line_only_true_grade', grade, '.pdf'),
         g, w = 8, h = 8)

  # density plot of probabilities
  with_cutoff_line = combined_pred %>% group_by(model_name, split) %>%
    mutate(rank = row_number(desc(predicted_score)),
           cutoff = rank <= n() * 0.10) %>%
    group_by(model_name, split, cutoff) 
  # separate into two pieces to avoid possible bug?
  with_cutoff_line = with_cutoff_line %>%
    mutate(cutoff_val = ifelse(cutoff, last(predicted_score), NA)) %>%
    # reorder set names
    ungroup() %>%
    mutate(split = factor(split, levels = c('train', 'val', 'test')))
  
  g = ggplot(with_cutoff_line, aes(x = predicted_score, fill = factor(true_label),
                                   color = factor(true_label))) + 
    facet_grid(model_name~split) +
    geom_freqpoly() + ylim(0, 50) + geom_vline(aes(xintercept = cutoff_val)) +
    ggtitle("Density of Pred Probas w/cutoff lines")
  ggsave(plot = g,
         filename = paste0('compare_RF_logit_diffs/density_of_pred_probas_w_10pcnt_cutoff_grade', grade, '.pdf'),
         w = 10, h = 8)
}