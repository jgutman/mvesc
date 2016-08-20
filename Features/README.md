# Feature Generation Modules

This folder contains the scripts for extracting both features and outcome labels to be used for the prediction problem. 
These are stored in the database.

### How to Generate features and outcomes
Only 2 Python scripts are needed to be run, and all the rest will be called in these 2 Python scripts.
 * `generate_absence_features.py` 
 * `generate_outcome.py`
 
### Label/Outcome Definitions

We have several possible definition schemes for choosing outcomes. We create a column for each possible defintion in the database.
(More description will be added later)
 * `not_on_time`
 * `is_dropout`
 * `definite`
 * `definite_plus_ogt`

### Feature Descriptions
absence:
  * `absence*`
  * `absence_unexcused*`
  * `tardy*`
  * `tardy_unexcused*`
  * `medical*`
  * `absence_consec*`
  * `tardy_consec*`
  * `absence_wkd_1*`
  * `absence_wkd_2*`
  * `absence_wkd_3*`
  * `absence_wkd_4*`
  * `absence_wkd_5*`
  * `tardy_wkd_1*`
  * `tardy_wkd_2*`
  * `tardy_wkd_3*`
  * `tardy_wkd_4*`
  * `tardy_wkd_5*`

demographics:
  * `ethnicity`
  * `gender`

grades:
  * `gpa*`
  * `language_gpa*`
  * `stem_gpa*`
  * `humanities_gpa*`
  * `art_gpa*`
  * `health_gpa*`
  * `future_prep_gpa*`
  * `interventions_gpa*`
  * `num_stem_classes*`
  * `num_humanities_classes*`
  * `num_art_classes*`
  * `num_health_classes*`
  * `num_future_prep_classes*`
  * `num_interventions_classes*`
  * `num_language_classes*`
  * `percent_passed_pf_classes*`
  * `num_pf_classes*`
  * `gpa_district*`

mobility:
  * `n_addresses_to*`
  * `n_districts_to*`
  * `n_cities_to*`
  * `n_records_to*`
  * `avg_address_change_to*`
  * `avg_district_change_to*`
  * `avg_city_change_to*`
  * `street_transition_in*`
  * `district_transition_in*`
  * `city_transition_in*`
  * `mid_year_withdraw*`

oaa_normalized:
  * `read_normalized_gr_3`
  * `read_percentile_gr_3`
  * `read_pl_gr_3`
  * `math_normalized_gr_3`
  * `math_percentile_gr_3`
  * `math_pl_gr_3`
  * `read_normalized_gr_4`
  * `read_percentile_gr_4`
  * `read_pl_gr_4`
  * `math_normalized_gr_4`
  * `math_percentile_gr_4`
  * `math_pl_gr_4`
  * `read_normalized_gr_5`
  * `read_percentile_gr_5`
  * `read_pl_gr_5`
  * `math_normalized_gr_5`
  * `math_percentile_gr_5`
  * `math_pl_gr_5`
  * `socstudies_normalized_gr_5`
  * `socstudies_percentile_gr_5`
  * `socstudies_pl_gr_5`
  * `science_normalized_gr_5`
  * `science_percentile_gr_5`
  * `science_pl_gr_5`
  * `read_normalized_gr_6`
  * `read_percentile_gr_6`
  * `read_pl_gr_6`
  * `math_normalized_gr_6`
  * `math_percentile_gr_6`
  * `math_pl_gr_6`
  * `read_normalized_gr_7`
  * `read_percentile_gr_7`
  * `read_pl_gr_7`
  * `math_normalized_gr_7`
  * `math_percentile_gr_7`
  * `math_pl_gr_7`
  * `read_normalized_gr_8`
  * `read_percentile_gr_8`
  * `read_pl_gr_8`
  * `math_normalized_gr_8`
  * `math_percentile_gr_8`
  * `math_pl_gr_8`
  * `science_normalized_gr_8`
  * `science_percentile_gr_8`
  * `science_pl_gr_8`

snapshots:
  * `disadvantagement*`
  * `disability*`
  * `district*`
  * `gifted*`
  * `iss*`
  * `oss*`
  * `limited_english*`
  * `special_ed*`
  * `status*`
  * `discipline_incidents*`
  * `section_504_plan*`

intervention:
  * `extracurr_program*`
  * `post_secondary*`
  * `academic_inv*`
  * `atheletics*`
  * `placement*`
  * `spec_instruc*`
  * `vocational*`
  * `academic_intracurr*`
  * `school_program*`
  * `titlei*`
  
An asterisk after a feature name indicates that it has a feature for each grade level.
The scripts to generate each set of features can be found in generate_features.py.
