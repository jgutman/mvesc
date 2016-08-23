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

