# Prediction Modeling & Results

This folder contains the code to choose specific features to include in the model, the types of classifiers to run, and loop through these models, outputting and summarizing results.

## Running Instructions

Provide a model options file (see required attributes in `model_options.yaml`) and a grid search options file (see required attributes in `grid_search_full.yaml`). Run these models as

`python estimate_prediction_model.py -m model_options.yaml -g grid_search_full.yaml`.

### Choosing Features to Include

In the appropriate `model_options.yaml` file, specify all relevant features as:

`table_a: [feature1, feature2, feature3]`

`table_b: [feature4, feature5]`

`table_c: [feature6]`

### Estimating the Prediction Model
Specify the types of classifiers to include in  `model_classes_selected` as a list, and specify the hyperparameter values for each model to search over in the `grid_options.yaml` file. Specify which cohorts to include in training and test sets, and the type of cross-validation scheme that should be used.

### Saving the Model Details & Results

For analysis and improvement of our models, it's important that we record all of
* the inputs and parameters used to estimate the prediction model
* the results of the prediction performance

We measure performance in several ways. We primarily focus on precision and recall, especially because our early warning risk prediction problem is imbalanced, with a large majority of students not labeled as at risk.
`save_reports.py` generates detailed markdown reports and summary tables for each model run.
