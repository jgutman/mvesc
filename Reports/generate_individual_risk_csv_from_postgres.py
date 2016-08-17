import os, sys
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0, parentdir)
from mvesc_utility_functions import *
import pandas as pd


### Generate a CSV for our partner
def main():
    schema, table = 'model', 'individual_risk_scores_factors'
    csvfile = 'current_student_predictions_logit_20160817.csv'
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            sql_select = """
            select student_lookup, grade, school_year, school_code, district,
            risk_score, risk_level, risk_factor_1, risk_factor_2, risk_factor_3, 
            risk_factor_1_value, risk_factor_2_value, risk_factor_3_value
            from {s}.{t}
            order by grade, district, school_code, risk_score desc;
            """.format(s=schema, t=table)
            df = pd.read_sql_query(sql_select, conn)
            
    df.to_csv(csvfile, index=False)
    print("Results Saved to", csvfile)


if __name__=='__main__':
    main()


