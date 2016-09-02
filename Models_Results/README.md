# Prediction Modeling & Results

This folder contains the code to choose specific features to include in the model, the types of classifiers to run, and loop through these models, outputting and summarizing results.

## Running Instructions

Provide a model options file (see required attributes in `example_template_dict.py`) and a grid search options file (see required attributes in `grid_search_full.yaml`). Also provide the output directory for generating the markdown reports summarizing each model run. Run these models as

`python estimate_prediction_model.py -m model_options.yaml -g grid_search_full.yaml -o ../Reports`.

### Saving the Model Details & Results

For analysis and improvement of our models, it's important that we record all of
* the inputs and parameters used to estimate the prediction model
* the results of the prediction performance

We measure performance in several ways. We primarily focus on precision and recall, especially because our early warning risk prediction problem is imbalanced, with a large majority of students not labeled as at risk.
`save_reports.py` generates detailed markdown reports and graphs, and write_to_database writes summary information to `model.reports` for each model run. If the `write_to_databse` option is set to true, then all the predictions and all the feature scores are also written to the database for easy analysis. 

### Feature Importances and Individual Risks

`generate_individual_risks` creates a new table (as well as saving a csv) for a given model which contains individual risk scores and individual risk factors for all current students. For logit models this process is very quick, but for other model types a different process is used for calculating individual feature importances and is very slow. 
