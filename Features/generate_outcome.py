""" Generate Outcome table
SQL command is used to drop and create outcome table

"""

import os
from os.path import isfile, join, abspath, basename
from optparse import OptionParser
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import json

import sys
parentdir = os.path.abspath('/home/xcheng/mvesc/ETL')
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *


if __name__=='__main__':
    schema, table = "model" ,"outcome"
    source_schema, source_table = "clean", "wrk_tracking_students"
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            sql_drop_table = 'drop table if exists {schema}.{table};'.format(schema=schema, table=table)
            cursor.execute(sql_drop_table); connection.commit()
            sql_create_table = """
            create table model.outcome as 
            select * from 
            (   select student_lookup,  
                case
                    when outcome_category='on-time' then 0
                    else 1
                end as not_on_time, 
                case
                    when outcome_category='dropout' then 1
                    else 0
                end as is_dropout, 
                case
                    when "2006"=9 then 2006
                    when "2007"=9 then 2007
                    when "2008"=9 then 2008
                    when "2009"=9 then 2009
                    when "2010"=9 then 2010
                    when "2011"=9 then 2011
                    when "2012"=9 then 2012
                    else null
                end as cohort_9th
                from clean.wrk_tracking_students
                where outcome_category is not null
            ) all_cohorts
            where cohort_9th is not null
            order by cohort_9th, not_on_time desc, is_dropout desc;
            """
            cursor.execute(sql_create_table); connection.commit()
    print("""- Table "{schema}"."{table}" created! """.format(schema=schema, table=table))
