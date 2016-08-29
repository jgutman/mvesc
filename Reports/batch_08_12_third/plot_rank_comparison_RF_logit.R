### Summarizing Third Batch Run 08_12 ###

# Get the reference to the `reports` table
#   sets the correct working directory to make reports
#   function automatically gets rid of debug rows
#   and redundant rows with multiple cv_criterion in first batch
#   and automatically loads appropriate packages
#   and allows a custom where statement to get the appropriate batch
setwd('~/mvesc/Reports/batch_08_12_third/')

### Compare Students Across Model Predictions ###
# ** Batch Four does this for all grade levels **
# get filenames of the top 1 for RF and logit on
#   label = definite_plus_ogt
#   features = all
#   prediction_grade = 7
#   ranked by = cv_score

###########
# IGNORE #
# OLD: DATABASE HAS REMOVED THE PREDICTIONS FROM BATCH THREE
# top_rf_logit = reports_ref %>%
#   filter(model_name %in% c('RF', 'logit'),
#          prediction_grade == 7,
#          label == 'definite_plus_ogt') %>%
#   grab_top_performing('cv_score', 1, c('model_name')) %>% collect()
# 
# # get predictions for each model
# predictions_ref = tbl(pg_db, dplyr::sql('SELECT * FROM model.predictions'))
# rf_pred = predictions_ref %>% filter(filename == top_rf_logit$filename[top_rf_logit$model_name == 'RF'][[1]]) %>%
#   collect()
# logit_pred = predictions_ref %>% filter(filename == top_rf_logit$filename[top_rf_logit$model_name == 'logit'][[1]]) %>%
#   collect()
#############

# BATCH THREE TOP MODELS SAVED IN RDS FOLDERS
# look at individual students
if (!exists('rf_pred')) {
  rf_pred = readRDS('individual_pred_probas/top_rf_pred.rds'); 
  logit_pred = readRDS('individual_pred_probas/top_logit_pred.rds');
}

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

# BEGIN PLOTS #
# based on rank diff
g = ggplot(by_id_diff, aes(x = rank_diff_order, y = rank_diff, color = factor(true_label))) + 
  geom_point(position = position_jitter(width = 10, h = 10)) +
  facet_wrap(~split) + ggtitle("RF Rank - Logit Rank (neg = RF puts more risky)")
ggsave('compare_RF_logit_diffs/dist_of_rank_diff.pdf', g, w = 8, h = 8)

# scatter diff versus logit predictions
g <- ggplot(by_id_diff, aes(x = lr_rank, y = rf_rank, color = factor(true_label))) + 
  geom_point() + geom_smooth() + geom_abline(slope = 1, intercept = 0) +
  facet_wrap(~split) + ggtitle("RF Rank vs Logit Rank") + theme_bw()
g
ggsave(plot = g, 
       filename = 'compare_RF_logit_diffs/rank_scatterplot_w_trend_line.pdf', w = 8, h = 8)

# only with the true labels
g <- ggplot(filter(by_id_diff, true_label == 1),
            aes(x = lr_rank, y = rf_rank, color = factor(true_label))) + 
  geom_point() + geom_smooth() + geom_abline(slope = 1, intercept = 0) +
  facet_wrap(~split) + ggtitle("RF Rank vs Logit Rank (only ground truth labels)") + theme_bw()
g
ggsave(plot = g, 
       filename = 'compare_RF_logit_diffs/rank_scatterplot_w_trend_line_only_true.pdf', w = 8, h = 8)

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
       filename = 'compare_RF_logit_diffs/density_of_pred_probas_w_10pcnt_cutoff.pdf',
       w = 10, h = 8)