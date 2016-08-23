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


### Future Work: Plot Train, Val, and Test Performance Together ###


### Comparing the downsampling rates ###
# BUG: MISSING COLUMN IN DOWNSAMPLING RATE
# downsample_compare <- reports_ref %>%
#   grab_top_performing('val_precision_5_15', 1, 
#                       c(vec_to_group_on, 'downsample')) %>%
#   filter(model_name != 'DT', label == 'definite_plus_ogt') %>%
#   collect_and_ggplot_obj(vec_to_gather = c('val_precision_5_15',
#                                            'test_precision_5_15'),
#                          vec_to_group_on = c('model_name', 'prediction_grade',
#                                              'downsample'),
#                          xvar = 'prediction_grade',
#                          color_var = 'downsample',
#                          extra_var = 'label')