### Summarizing Third Batch Run 08_12 ###

# Load required credentials and libraries
library("plyr"); library("dplyr"); library("ggplot2");
library("tidyr"); library("stringr"); library("RPostgreSQL")
library("lazyeval"); library("lubridate")
# getting postgres database credentials
pgpass = str_split(read.table("/mnt/data/mvesc/pgpass")[1,1], ":")[[1]]
# connecting to db
pg_db = src_postgres(dbname = pgpass[3], host = pgpass[1],
                     port = pgpass[2], user = pgpass[4], password = pgpass[5])

# Get the reference to the `reports` table
reports_ref = tbl(pg_db, dplyr::sql('SELECT * FROM model.reports'))
# set wd
setwd('~/mvesc/Reports/batch_third_0812/')

# get rid of overall redundancy
# since some rows contain duplicates, remove by choosing one of the four
#   cv_criterion
# only use non-debug rows
batch_third = reports_ref %>% filter(cv_criterion == 'custom_precision_5_15',
                                 debug == FALSE,
                                 timestamp > '2016-08-13 01:00:00',
                                 feature_categories == 'absence, demographics, grades, intervention, mobility, oaa_normalized, snapshots')

# Functions #
grab_top_performing = function(ref, score_col, top_num,
                               vec_of_group_by_col) {
  top_dat = ref %>% group_by_(.dots = vec_of_group_by_col) %>%
    mutate_(rank = interp(~row_number(desc(v)), v = as.name(score_col))) %>%
    filter(rank <= top_num)
  top_dat
}

gather_recall_3_10 = function(df, vec_to_gather, vec_to_group_on){
  df %>% ungroup() %>% gather_("recall_k", "recall", vec_to_gather) %>%
    separate(recall_k, c("dataset", "metric_type", "k_pcnt_intervene"), sep = "_") %>%
    group_by_(.dots = vec_to_group_on) %>% 
    summarise(avg_recall = mean(recall)) %>%
    ungroup() %>%
    mutate(k_pcnt_intervene = as.numeric(as.character(k_pcnt_intervene)),
           prediction_grade = factor(prediction_grade))
}

## Compare Models on CV_Scheme ##
compare_cv_scheme = function(ref, score_col){
  # grab top model names and cv_scheme
  top_ref = grab_top_performing(batch_third, "cv_score", 1,
                                c("model_name", "prediction_grade", "label"))
  test_df = top_ref %>% select(model_name, prediction_grade, label,
                          parameters,
                          cv_score, val_precision_5_15, test_precision_5_15) %>%
    collect()
  
  
  plot_df = gather_recall_3_10(test_df, c("val_precision_5_15", "test_precision_5_15"),
                               c("model_name", "prediction_grade", 
                                     "metric_type", "label", "k_pcnt_intervene")) %>%
    filter(!model_name %in% c('DT', 'ET'))
  # ggplot by prediction_grade
  g <- ggplot(filter(plot_df, model_name %in% c('logit', 'RF', 'SVM')), 
              aes(x = prediction_grade,
                           y = avg_recall,
                           color = model_name,
                           group = model_name))
  
  g + geom_point(size = 4) + facet_wrap(~ label, #scales = "free_y",
                                ncol = 3) + geom_line()
  
}

compare_by_cv_score = function(ref, score_col){
  # grab top model names and cv_scheme
  top_ref = grab_top_performing(batch_third, "cv_score", 5,
                                c("model_name", "prediction_grade", "label"))
  df = top_ref %>% select(model_name, prediction_grade, label, rank,
                          parameters, cv_score) %>% collect() %>% filter(model_name != 'DT')
  
  z <- ggplot(df, aes(x = rank, y = cv_score, color = model_name)) + 
    geom_point(size = 4) + facet_wrap(~prediction_grade + label, ncol = 3)
}


### Compare Models Performance Overall ###
compare_models_overall = function(ref, score_col){
  # grab top model names and cv_scheme
  top_ref = grab_top_performing(ref, "cv_score", 1,
                                c("model_name", "cv_scheme", "prediction_grade"))
  df = collect(top_ref %>% select(model_name, cv_scheme, prediction_grade, label,
                                  cv_score, val_recall_3, val_recall_5, val_recall_10,
                                  test_recall_3, test_recall_5, test_recall_10) %>%
                 filter(label == 'not_on_time'))
  
  
  plot_df = gather_recall_3_10(df, c("model_name", "prediction_grade", 
                                     "metric_type", "k_pcnt_intervene"))
  
  # ggplot by prediction_grade
  g <- ggplot(plot_df, aes(x = k_pcnt_intervene,
                           y = avg_recall,
                           color = model_name,
                           group = model_name))
  
  g + geom_point() + facet_wrap(~prediction_grade, nrow = 1) + geom_line()
}

# avg run time by model type
avg_run_time = batch_two %>% filter(label == "not_on_time") %>% group_by(model_name) %>% 
  summarise(mean_time = mean(time)) %>% collect()
print(avg_run_time, n = 10)

# avg run time of GB by parameters
avg_GB_time = batch_two %>% filter(label == "not_on_time",
                                    model_name == 'GB') %>%
  group_by(parameters) %>% 
  summarise(mean_time = mean(time)) %>% 
  arrange(desc(mean_time)) %>% collect()
print.data.frame(avg_GB_time)


### Compare Given Model to Its Parameters ###
look_at_one_model_parameters = function(ref, model) {
  model_ref = ref %>% filter(model_name == model,
                             label == 'not_on_time') %>%
    select(model_name, parameters, prediction_grade, cv_score, 
           val_recall_3, val_recall_5, val_recall_10,
           test_recall_3, test_recall_5, test_recall_10)
  
  df = collect(model_ref) 
  
  gathered = gather_recall_3_10(df, c("model_name", "prediction_grade", 
                                      "metric_type", "k_pcnt_intervene",
                                      "parameters"))
  
  plot_df = gathered %>% separate(parameters,
                            into = paste0("p", seq(4)),
                            sep = "; ", extra = 'merge') %>%
    unite(p1p2, p1, p2, remove = F)
  
  
  # ggplot by prediction_grade
  g <- ggplot(filter(plot_df, prediction_grade == 6), 
              aes(x = k_pcnt_intervene,
                           y = avg_recall,
                           color = p1,
                           group = p1p2,
                           linetype = p2))
  
  g + geom_point() + facet_grid(p3~p4) + geom_line() + ggtitle(paste(model, "parameters"))
  
  ## or
  g <- ggplot(filter(gathered, prediction_grade == 6),
              aes(x = k_pcnt_intervene, y = avg_recall, 
                  color = parameters, group = parameters))
  g + geom_point() + geom_line() + theme(legend.position="none")
}


### (1) Plot the Overall Distribution for each Model Name ###
#   dot plot of all the runs for each model
#   group by model type and get the top performances in a certain category
distrib_for_model = function(df, score_col, top_num, 
                             shape_col, outcome_label,
                             summarize = FALSE,
                             suggested_title = NA) {
  model_groups = df %>% filter(label == outcome_label) %>%
    select_(score_col, shape_col, 
            "model_name", "feature_categories") %>%
    group_by(model_name, feature_categories) %>%
    mutate_(rank = interp(~row_number(desc(v)), v = as.name(score_col))) %>%
    filter(rank < top_num)
  plot_df = collect(model_groups) %>% ungroup(feature_categories)
  
  # manually adjust the values in feature_categories
  plot_df = plot_df %>% mutate(feature_name = 
                       ifelse(str_count(feature_categories, ",") > 4,
                              "full_features",
                              feature_categories))
  
  if (summarize) {
    plot_df = plot_df %>% group_by(model_name, feature_name) %>%
      summarise_(plot_score = interp(~mean(v), v=as.name(score_col)))
  } else {
    plot_df = plot_df %>% rename_("plot_score" = score_col)
  }
  if (is.na(suggested_title)){
    suggested_title = paste("All Runs", score_col, "keep only top", top_num,
                            "of each feature;\nuse label", outcome_label,
                            "\nignoring grade_range, impute, scaling, cv_scheme info")
  }
  
  # refactor based on best "full_features"
  ordering_models = plot_df %>% filter(feature_name == 'full_features') %>%
    arrange(desc(plot_score)) %>% distinct(model_name)
  # refactor plot_df model_names based on this
  plot_df = plot_df %>% ungroup() %>%
    mutate(model_name = factor(model_name,
                               levels = ordering_models$model_name))
  
  # dot plot by model_type
  g <- ggplot(plot_df, aes_string("model_name", "plot_score",
                             color = "feature_name",
                             group = "feature_name")) +
    geom_line() +
    theme_bw() + ylab(score_col) +
    ggtitle(suggested_title)
  if (summarize) {
    g = g + geom_point(position = position_jitter(height = 0, width = 0.1),
                       size = 8)
  } else {
    g = g + geom_point(position = position_jitter(height = 0),
                       size = 2)
  }
  g
}

for (metric in c('val_precision_5')){
  for (outcome in c('not_on_time', 'definite', 'is_dropout')) {
    # top 25
    g = distrib_for_model(reports, metric, 25, 'cv_scheme', outcome)
    ggsave(plot = g, 
           filename = paste0('all_model_dist/dist_', metric,
                             '_', outcome, '_top25.pdf'),
           w = 8, h = 8)
    # top 12
    g = distrib_for_model(reports, metric, 12, 'cv_scheme', outcome)
    ggsave(plot = g, 
           filename = paste0('all_model_dist/dist_', metric,
                             '_', outcome, '_top12.pdf'),
           w = 8, h = 8)
    # save summarized top 12
    g = distrib_for_model(reports, metric, 12, 'cv_scheme', outcome,
                          summarize = T,
                          suggested_title = paste("Avgd Model Performance by Feature
                          on label", outcome, "using metric", metric))
    g = g + theme(text = element_text(size=20)) +
      ylab(metric)
    # ggsave(plot = g, 
    #        filename = paste0('all_model_dist/avgd_dist_', metric,
    #                          '_', outcome, '_top12.pdf'),
    #        w = 8, h = 8)
  }
}

for (metric in c('val_precision_5')){
  for (outcome in c('not_on_time', 'definite', 'is_dropout')) {
    # top 25
    g = distrib_for_model(reports, metric, 25, 'cv_scheme', outcome)
    ggsave(plot = g,
           filename = paste0('all_model_dist/dist_', metric,
                             '_', outcome, '_top25.pdf'),
           w = 8, h = 8)
    # top 12
    g = distrib_for_model(reports, metric, 12, 'cv_scheme', outcome)
    ggsave(plot = g,
           filename = paste0('all_model_dist/dist_', metric,
                             '_', outcome, '_top12.pdf'),
           w = 8, h = 8)
  }
}

### (2) For each specific model, plot how grade range influences ###

#   facet ON feature
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
  plot_df = collect(filtered_ref)
  # manually adjust the values in feature_categories
  plot_df = plot_df %>% mutate(feature_name = 
                                 ifelse(str_count(feature_categories, ",") > 4,
                                        "all_features",
                                        feature_categories))
  
  # uniting imputation & scaling
  plot_df = plot_df %>% unite(imp_scal, c(imputation, scaling))
  
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
all_models = collect(reports %>% select(model_name) %>% distinct())
for (specific_model in all_models$model_name) {
  for (metric in c('val_precision_5')){
    for (outcome in c('not_on_time', 'definite', 'is_dropout')) {
      g = plot_each_model_on_grade(reports, metric, specific_model, outcome)
      
      ggsave(plot = g, 
             filename = paste0('each_model_by_grade_range_features/',
                               specific_model, '_', metric, '_', outcome,
                               '.pdf'),
             w = 8, h = 8)
    }
  }
}


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
            "cv_scheme", "feature_grades", "model_name", "timestamp")
  # get into memory
  plot_df = collect(filtered_ref)
  # filter to keep only the first batch
  plot_df = plot_df %>% filter(yday(timestamp) <= 222) %>%
    select(-timestamp)
  
  # manually adjust the values in feature_categories
  plot_df = plot_df %>% mutate(feature_name = 
                                 ifelse(str_count(feature_categories, ",") > 4,
                                        "all_features",
                                        feature_categories))
  # manually adjust the values in feature_categories
  plot_df = plot_df %>% mutate(feature_name = 
                                 ifelse(str_count(feature_categories, ",") > 4,
                                        "all_features",
                                        feature_categories))
  
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
                  "\n with cv_scheme in color",
                  "\ngiven", impute_type, scale_type))
  g # return
}

# LOOP OVER OUTCOMES #
for (metric in c('val_precision_5')){
  for (outcome in c('not_on_time', 'definite', 'is_dropout')) {
    g = plot_multiple_model_on_grade(reports, metric,
                                     c('logit', 'RF', 'GB', 'SVM'),
                                     outcome, 'median_plus_dummies',
                                     'robust')
    ggsave(plot = g, 
           filename = paste0('compare_across_models/lr_rf_gb_svm_',
                             metric, '_', outcome, '.pdf'),
           w = 8, h = 8)
  }
}

### (4) Comparing Train Test & Val Performance ###
get_top_n_train_performance = function(df)


#### OLD Plots ###

### (1) Save overall plots on distribution of results ###
cv_info_only = reports %>% select(cv_scheme, cv_score, cv_criterion, feature_categories) %>%
  filter(cv_criterion == 'custom_precision_5') %>% 
  select(cv_scheme, cv_score, feature_categories)
plot_df = collect(cv_info_only)
ggplot(plot_df, aes(x = cv_score, fill = cv_scheme)) + geom_density(alpha = 0.25) +
  facet_wrap(~feature_categories)

density_plot_scores = function(df, score_col, color_col, facet_col){
  score_info = df %>% select_(color_col, score_col, facet_col)
  plot_df = collect(score_info)
  g <- ggplot(plot_df, aes_string(x = score_col, fill = color_col)) +
    geom_density(alpha = 0.25) +
    facet_wrap(as.formula(paste('~', facet_col))) +
    ggtitle(paste(score_col, color_col, facet_col, sep = "/"))
  print(g)
}
density_plot_scores(reports, "val_recall_5", "cv_scheme", "feature_categories")
