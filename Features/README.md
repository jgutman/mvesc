# Feature Generation Modules

This folder contains the scripts for extracting both features and outcome labels to be used for the prediction problem.
These are stored in the database.

### How to Generate features and outcomes
Only 2 Python scripts are needed to be run, and all the rest will be called in these 2 Python scripts.
 * `generate_outcome.py`
 * `generate_features.py`

These 2 scripts depend on:
 1. ETL utilities functions: `ETL/mvesc_utility_functions.py`
 2. feature utilities functions: `Features/feature_utilities.py`
 3. all sub-scripts to generate a certain type of features:
    * `./generate_demographic_features.py`
    * `./generate_snapshot_features.py`
    * `./generate_mobility_features.py`
    * `./generate_consec_absence_columns.py`
    * `./generate_absence_features.py`
    * `./generate_gpa.py`
    * `./generate_normalized_oaa_pandas.py`
    * `./generate_intervention_features.py`

### Label/Outcome Definitions

We have several possible definition schemes for choosing outcomes. We create a column for each possible definition in the database.
 * `not_on_time`
    - 4-year-graduates marked as 0, otherwise 1
    - pros: easy to define
    - cons: all uncertain students marked as 1 (at-risk)
 * `is_dropout`
    - `dropout` indicated in withdrawal code marked as 1, otherwise 0
    - pros: easy to define
    - cons: too few definite labels, all uncertain students marked as 0 (not at-risk)
 * `definite`
    - `dropout` marked as 1; 4-year-graduate marked as 0
    - pros: easy to define; reliable to use
    - cons: too few class 1's especially for some cohorts
 * `definite_plus_ogt`
    - `dropout` and students with low OGT scores, many absences, or low grades marked as 1; others marked as 0
    - pros: number of 1 and 0 are most reasonable (around 10%)
    - cons: need to pick threshold semi-manually (analysis in find_cutoffs.sql)

### Feature Descriptions
A full list of all features can be found in all_features.yaml, and any new feature must be manually added to that list before it can be used.
An asterisk after a feature name indicates that it has a feature for each grade level (formatted as `_gr_x` for some grade level x).
The scripts to generate each set of features is called in `generate_features.py`.
