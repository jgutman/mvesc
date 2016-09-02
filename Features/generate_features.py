# Inital v0 of a script to take in options file and generate
#	the corresponding outcomes and features for prediction.
# Generates all possible features we're considering

import sys

import generate_demographic_features
import generate_snapshot_features
import generate_mobility_features
import generate_absence_features
import generate_gpa
import generate_normalized_oaa_pandas
import generate_intervention_features
from feature_dependent_outcome import add_outcome

def main(argv):
    
    clean_schema = argv[0]
    model_schema = argv[1]
    
    print("--- working on generating model.demographics table ... ")
    generate_demographic_features.main([clean_schema,model_schema])

    print("--- working on generating model.snapshots table ... ")
    generate_snapshot_features.main([clean_schema,model_schema])

    print("--- working on generating model.absence table ... ")
    generate_absence_features.main([clean_schema,model_schema])

    print("--- working on generating model.mobility table ... ")
    generate_mobility_features.main([clean_schema,model_schema])

    print("--- working on generating model.grades table ... ")
    generate_gpa.main([clean_schema,model_schema])

    print("--- working on generating model.oaa_normalized table ... ")
    # a bit slow due to for loop and writing to postgres from pandas
    generate_normalized_oaa_pandas.main([clean_schema,model_schema])

    print("--- working on generating model.intervention table ... ")
    generate_intervention_features.main([clean_schema,model_schema])
    
    # use feature utilities to execute the sql file
    print("--- adding a new outcome to the model.outcome table based on ogt, absences, gpa")
    add_outcome(clean_schema, model_schema)

if __name__=='__main__':
    main(sys.argv[1:])
