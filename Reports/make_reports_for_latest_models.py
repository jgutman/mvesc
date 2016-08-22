import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")

sys.path.insert(0, os.path.join(base_pathname, "ETL"))
sys.path.insert(0, os.path.join(base_pathname, "Models_Results"))

from mvesc_utility_functions import postgres_pgconnection_generator
from save_reports import write_model_report
from make_predictions_for_unlabeled_students import read_in_model

def main():

if __name__ == '__main__':
    main()
