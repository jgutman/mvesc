# Prediction Modeling & Results

This folder contains the code to choose specific features to include in the model, the types of classifiers to run, and loop through these models, outputting and summarizing results.

## Definitions

'Cohort' does _not_ refer to the year of expected graduation upon enrollment into grade 9. It is used instead to denote the academic year in which a student is enrolled in a specific grade; for example, a student who is in 'grade 9 cohort for 2012' is enrolled in grade 9 in the academic year 2012.

'Academic year' refers to the _fall_ calendar year; thus, the school year 2011-2012 would be listed as 2011.

## Running Instructions

Provide a model options file (see required attributes in `example_template_dict.py`) and a grid search options file (see required attributes in `grid_search_full.yaml`). Also provide the output directory for generating the markdown reports summarizing each model run. Run these models as:

`python estimate_prediction_model.py -m model_options.yaml -g grid_search_full.yaml -o ../Reports`.

The `batch_name` option also makes it easy to run batches of models in a loop - for exampls of these scripts, see the `batch_1` through `batch_4` folders. Further documentation of each of these batches is available in the technical plan. Some of these runs used previous iterations of the model options files, so earlier ones may not run, but they are included here for documentation of the different options we tried. All generated yaml files are saved in the `model_options` folder, and the `final_models` subfolder contains the yaml files for the models which we found to be the best performing.

### Saving the Model Details & Results

For analysis and improvement of our models, it's important that we record all of
* the inputs and parameters used to estimate the prediction model
* the results of the prediction performance

We measure performance in several ways. We primarily focus on precision and recall, especially because our early warning risk prediction problem is imbalanced, with a large majority of students not labeled as at risk.
`save_reports.py` generates detailed markdown reports and graphs, and write_to_database writes summary information to `model.reports` for each model run. If the `write_to_databse` option is set to true, then all the predictions and all the feature scores are also written to the database for easy analysis (into model.predictions and model.feature_scores; the latter are the feature importances). All experiments are identified by a filename, which is the combination of the experiment's YAML's batch_name plus the YAML's name parameters plus the model name.

### Feature Importances and Individual Risks

`generate_individual_risks` creates a new table (as well as saving a csv) for a given model which contains individual risk scores and individual risk factors for all current students (defined by the `CURRENT_YEAR` in the repo's config file). For logit models this process is very quick, but for other model types a different process is used for calculating individual feature importances and is very slow. 

`generate_individual_risks` takes either option '-f' with a particular filename to generate the table for one model, or -m with 'logit' or 'RF' to generate the table for the best model for each grade level for that model class.
