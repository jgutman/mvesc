### Summarizing Fourth Batch Run 08_17 ###

reports_ref = load_table_ref('~/mvesc/Reports/batch_08_17_fourth/',
                             'custom_precision_5_15',
                             where_statement = "where batch_name like '08_17_2016%'")

for (grade in seq(6, 10)) {
  by_id_diff = get_rank_comparison_df(reports_ref, "definite_plus_ogt",
                                      grade, "cv_score")
  make_and_save_rank_plots(by_id_diff, grade)
}