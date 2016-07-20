""" Kill idle queries of a database

Usage: 
- $ python kill_idle_queries.py
  * kill idle queries in mvesc.dssg.io;

- $ python kill_idle_queries.py -d db_box
  * kill idle queries in database server `db_box`
"""

import os, sys
from optparse import OptionParser
import pandas as pd
pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)
from mvesc_utility_functions import *

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('-d','--database', dest='database',
                      help="datebase to create kill idle pid; default 'mvesc' ")

    (options, args) = parser.parse_args()

    ### Parameters to entered from the options or use default####
    database = 'mvesc'
    if options.database:
        database = options.database
    
    with postgres_pgconnection_generator() as conn:
        with conn.cursor() as cursor:
            sql_get_activity = """SELECT usename, state, pid, query FROM pg_stat_activity 
            WHERE datname = '{database}';""".format(database=database)
            activity = pd.read_sql(sql_get_activity, conn)
            idle_pids = activity.pid[['idle' in st for st in activity.state]]
            for pid in idle_pids:
                sql_kill_idle = "select pg_terminate_backend({pid});".format(pid=pid)
                cursor.execute(sql_kill_idle)
                conn.commit()
                print("- SQL Query '{pid}' killed!".format(pid=pid))

