import igraph
from igraph import *
import cairo

import os, sys, imp

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

from mvesc_utility_functions import postgres_pgconnection_generator

def get_bucket_counts(cursor, tree, grade_begin, year_begin,
        schema = 'clean', tracking = 'wrk_tracking_students', grads = 'all_graduates',
        dropout_recovery_irns="IRN_DORP_GRAD_RATE1415", jvsd_irns="JVSD_Contact"):
    """
    Runs a sql query for each of the 18 buckets in the initialized tree graph.
    Gets the counts and lists of student lookup numbers for each bucket.
    Updates the tree attributes with sql query results.
    :param psycopg2.cursor cursor: a cursor to execute sql queries in postgres
    :param igraph.Graph tree: an empty tree Graph, returned by build_empty_tree
        (stores the results of queries in tree representation)
    :param str grade_begin: the grade level of the entering cohort in string format
    :param int year_begin: the school year of the entering cohort
    :param str schema: name of schema containing tracking table
    :param str tracking: name of wide student tracking table
    """

    # This function assumes wrk_tracking_students and all_graduates have been built correctly
    # Make sure they are up to date with latest builds!

    # total students in cohort
    cohort_total_query = """select distinct student_lookup from
        {schema}.{table} where "{year_begin}" = {grade_begin}
    """.format(schema=schema, table=tracking, year_begin=year_begin, grade_begin=grade_begin)
    update_tree_with_query(cursor, tree, cohort_total_query, "cohort total")
    #print(cohort_total_query)

    # students without a graduation date in all_graduates table
    not_graduated_total_query = """{parent_query} and student_lookup not in
        (select student_lookup from {schema}.{grads})
    """.format(parent_query=cohort_total_query, schema=schema, grads=grads)
    update_tree_with_query(cursor, tree, not_graduated_total_query, "no graduation date")
    #print(not_graduated_total_query)

    # students with a graduation date in all_graduates table
    graduated_total_query = """{parent_query} and student_lookup in
        (select student_lookup from {schema}.{grads})
    """.format(parent_query=cohort_total_query, schema=schema, grads=grads)
    update_tree_with_query(cursor, tree, graduated_total_query, "graduation date")
    #print(graduated_total_query)

    # students without a withdrawal reason in tracking table
    no_withdrawal_reason_query = """{parent_query} and withdraw_reason is null
    """.format(parent_query=not_graduated_total_query)
    update_tree_with_query(cursor, tree, no_withdrawal_reason_query, "no withdrawal reason")
    #print(no_withdrawal_reason_query)

    # students with withdrawal reason in tracking table
    withdrawal_reason_query = """{parent_query} and withdraw_reason is not null
    """.format(parent_query=not_graduated_total_query)
    update_tree_with_query(cursor, tree, withdrawal_reason_query, "withdrawal reason")
    #print(withdrawal_reason_query)

    # get expected graduation date given current cohort grade level and year
    try:
        grade = int(grade_begin)
    except ValueError:
        print("Bad cohort grade level")
    assert(grade > 0 and grade <= 12), "Bad cohort grade level"

    years_to_graduate = 13-grade
    expected_grad_year = year_begin + years_to_graduate
    truncated_graduates_query = graduated_total_query.split(')')[0]

    # students with graduation within 4 years
    grad_in_4years_query = """{parent_query} where graduation_date <= '{year}-09-01')
    """.format(parent_query=truncated_graduates_query, year=expected_grad_year)
    update_tree_with_query(cursor, tree, grad_in_4years_query, "4 year graduation")
    #print(grad_in_4years_query)

    # students with graduation within 5 years
    grad_in_5years_query = """{parent_query} where graduation_date <= '{year_late}-09-01'
        and graduation_date > '{year_ontime}-09-01')
    """.format(parent_query=truncated_graduates_query, year_ontime = expected_grad_year,
               year_late=expected_grad_year+1)
    update_tree_with_query(cursor, tree, grad_in_5years_query, "5 year graduation")
    #print(grad_in_5years_query)

    # students with graduation in more than 5 years
    grad_in_gt5years_query = """{parent_query} where graduation_date > '{year_late}-09-01')
    """.format(parent_query=truncated_graduates_query, year_late=expected_grad_year+1)
    update_tree_with_query(cursor, tree, grad_in_gt5years_query, "more than 5 years")
    #print(grad_in_gt5years_query)

    # students without a withdrawal reason or withdrawal date in tracking table
    no_withdrawal_date_query = """{parent_query} and district_withdraw_date is null
    """.format(parent_query=no_withdrawal_reason_query)
    update_tree_with_query(cursor, tree, no_withdrawal_date_query, "no withdrawal date")
    #print(no_withdrawal_date_query)

    # students without a withdrawal reason but have a withdrawal date in tracking table
    has_withdrawal_date_query = """{parent_query} and district_withdraw_date is not null
    """.format(parent_query=no_withdrawal_reason_query)
    update_tree_with_query(cursor, tree, has_withdrawal_date_query, "district withdrawal date")
    #print(has_withdrawal_date_query)

    # students whose withdrawal reason is not dropout or transferred (starts with withdrew or expelled)
    withdrawal_misc_reasons = """{parent_query} and withdraw_reason not like 'transfer%'
        and withdraw_reason not like 'dropout%' and withdraw_reason not like 'graduate%'
    """.format(parent_query=withdrawal_reason_query)
    update_tree_with_query(cursor, tree, withdrawal_misc_reasons, "misc withdrawal")
    #print(withdrawal_misc_reasons)

    # students who transferred with or without IRN
    transfer_any_query = """{parent_query} and withdraw_reason like 'transfer%'
    """.format(parent_query=withdrawal_reason_query)
    update_tree_with_query(cursor, tree, transfer_any_query, "transferred")
    #print(transfer_any_query)

    # students who dropped out
    dropout_withdrawal_reason = """{parent_query} and withdraw_reason like 'dropout%'
    """.format(parent_query=withdrawal_reason_query)
    update_tree_with_query(cursor, tree, dropout_withdrawal_reason, "dropout")
    #print(dropout_withdrawal_reason)

    # students who transferred with withdrawn to IRN provided
    transfer_hasIRN_query = """{parent_query} and withdrawn_to_irn is not null
    """.format(parent_query=transfer_any_query)
    update_tree_with_query(cursor, tree, transfer_hasIRN_query, "withdrawn to IRN")
    #print(transfer_hasIRN_query)

    # students who transferred with no withdrawn to IRN
    # check that student doesn't have a withdrawn to IRN in any record of the tracking table
    transfer_noIRN_query = """{parent_query} and student_lookup not in
        ({alternate_query})
    """.format(parent_query=transfer_any_query, alternate_query=transfer_hasIRN_query)
    update_tree_with_query(cursor, tree, transfer_noIRN_query, "no withdraw to IRN")
    #print(transfer_noIRN_query)

    # students who transferred to a dropout recovery program
    transfer_dropout_recovery = """{parent_query} and withdrawn_to_irn::int in
        (select distinct(district_irn) from public."{dropout_recovery}")
    """.format(parent_query=transfer_hasIRN_query, dropout_recovery=dropout_recovery_irns)
    update_tree_with_query(cursor, tree, transfer_dropout_recovery, "dropout recovery program")
    #print(transfer_dropout_recovery)

    # students who transferred to a JVSD
    transfer_JVSD_query = """{parent_query} and withdrawn_to_irn::int in
        (select distinct(irn) from public."{jvsd}")
    """.format(parent_query=transfer_hasIRN_query, jvsd=jvsd_irns)
    update_tree_with_query(cursor, tree, transfer_JVSD_query, "JVSD/career tech")
    #print(transfer_JVSD_query)

    # students who transferred to any other IRN
    transfer_hasIRN_other = """{parent_query} and student_lookup not in
        ({jvsd_query}) and student_lookup not in ({dropout_recovery_query})
    """.format(parent_query=transfer_hasIRN_query, jvsd_query=transfer_JVSD_query,
               dropout_recovery_query=transfer_dropout_recovery)
    update_tree_with_query(cursor, tree, transfer_hasIRN_other, "other Ohio IRN")
    #print(transfer_hasIRN_other)

    #print(tree.vs["description"])
    #print(tree.vs["count"])
    return tree

def draw_tree_to_file(tree, filename="test_tree_plot.png"):
    """
    Draws a tree object to file in given filename.
    Visual attributes and mappings of the tree are defined in this function.
    Tree attributes should be fully defined before calling this function.
    """

    # set root of the tree at vertex 0
    tree_layout = tree.layout_reingold_tilford(root=[0])
    # set color mappings for each node in visualized tree graph
    color_dict = {"non-terminal":"black", "exclude":"yellow", "dropout":"red",
        "uncertain":"green", "late":"blue", "on-time":"magenta"}
    visual_style = {}
    visual_style["vertex_size"] = 30
    visual_style["vertex_color"] = [color_dict[category]
        for category in tree.vs["outcomes"]]
    visual_style["vertex_label"] = ["{desc}\n{count}".format(
        desc=desc, count=count)
        for desc,count in zip(tree.vs["description"], tree.vs["count"])]
    visual_style["layout"] = tree_layout
    visual_style["vertex_label_dist"] = 2
    visual_style["bbox"] = (800, 800) # size of plot in pixels
    # margin needs to be big enough so text on the edges doesn't get cut off
    visual_style["margin"] = 60
    visual_style["vertex_label_size"] = 10 # font size
    try:
        plot(tree, filename, **visual_style)
    except TypeError:
        print("ignore TypeError - look for output file {name}".format(filename))

def build_empty_tree():
    """
    Builds an empty tree obj for outcome classification. Vertices are named and
    counts for each vertex are initialized at zero. Pass tree along with cursor
    to get_bucket_counts method to fill in student counts at each vertex.

    Tree contains 18 vertices and 17 edges
    4 vertex attributes: description, count, outcome, and students
    description: the fine-grained description of the bucket
    outcome: the rough category of the bucket
        (non-terminal, on-time, late, dropout, exclude, uncertain)
    count: the number of students in each bucket
    students: a list of student lookups in each (terminal) bucket
    """

    # Initialize tree structure
    num_vertices = 18
    tree = Graph()
    tree.add_vertices(num_vertices)
    tree.add_edges([(0,1), (0,2), (1,3), (1,4), (2,5), (2,6), (2,7),
        (3,8), (3,9), (4,10), (4,11), (4,12), (11,13), (11,14),
        (14,15), (14,16), (14,17)])
    tree.vs["description"] = ["cohort total", "no graduation date",
        "graduation date", "no withdrawal reason", "withdrawal reason",
        "4 year graduation", "5 year graduation", "more than 5 years",
        "no withdrawal date", "district withdrawal date", "misc withdrawal",
        "transferred", "dropout", "no withdraw to IRN", "withdrawn to IRN",
        "dropout recovery program", "JVSD/career tech", "other Ohio IRN"]
    assert(len(tree.vs["description"]) == num_vertices)
    tree.vs["count"] = [0] * num_vertices
    tree.vs["students"] = [None] * num_vertices

    # Map fine-grained bucket descriptions to rough outcome categories
    outcome_buckets = {}
    outcome_buckets["non-terminal"] = ["cohort total", "no graduation date",
        "graduation date", "no withdrawal reason", "withdrawal reason",
        "transferred", "withdrawn to IRN"]
    outcome_buckets["exclude"] = ["misc withdrawal"]
    outcome_buckets["dropout"] = ["dropout", "dropout recovery program"]
    outcome_buckets["uncertain"] = ["no withdrawal date",
        "district withdrawal date", "no withdraw to IRN", "JVSD/career tech",
        "other Ohio IRN"]
    outcome_buckets["late"] = ["5 year graduation", "more than 5 years"]
    outcome_buckets["on-time"] = ["4 year graduation"]

    # Reverse keys and values of outcome_buckets dict
    outcome_buckets_flipped = dict((outcome,
            [k for k,v in outcome_buckets.items() if outcome in v][0])
            for outcome in tree.vs["description"])

    # Set tree vertex attributes for broad categories defined above
    tree.vs["outcomes"] = [outcome_buckets_flipped[bucket]
            for bucket in tree.vs["description"]]

    #print(tree) # 18 vertices, 17 edges, 4 vertex attributes, 0 edge attributes
    return tree

def write_outcomes_to_database(cursor, tree, schema='clean', table='wrk_tracking_students'):
    """
    """
    for vertex_index in range(len(tree.vs)):
        outcome = tree.vs[vertex_index]["outcomes"]
        if (outcome != "non-terminal"):
            student_list = tree.vs[vertex_index]["students"]

            if (len(student_list) > 0):
                student_list_formatted = ", ".join([str(student) for student in student_list])
                bucket = tree.vs[vertex_index]["description"]

                update_bucket_query = """update {schema}.{table}
                    set outcome_bucket='{bucket}' where student_lookup in ({students});
                """.format(schema=schema, table=table, bucket=bucket, students=student_list_formatted)

                update_outcome_query = """update {schema}.{table}
                    set outcome_category='{outcome}' where student_lookup in ({students});
                """.format(schema=schema, table=table, outcome=outcome, students=student_list_formatted)

                cursor.execute(update_bucket_query)
                cursor.execute(update_outcome_query)

def update_tree_with_query(cursor, tree, query, desc_label):
    """
    """
    cursor.execute(query)
    student_list_results = cursor.fetchall() # a list of tuples of ints
    student_list = [student[0] for student in student_list_results] # a list of ints
    vertex_list = tree.vs.select(description=desc_label) # returns a vertex sequence
    assert(len(vertex_list) == 1) # descriptions should be unique, outcomes are not
    vertex_index = [v.index for v in vertex_list][0] # returns an int index of the vertex
    tree.vs[vertex_index]["students"] = student_list
    tree.vs[vertex_index]["count"] = len(student_list)

    # check that tree is updated, does not need to be returned (pass by reference)
    assert([v["count"] for v in vertex_list][0] == len(student_list_results))
    assert([v["students"] for v in vertex_list][0] == student_list)

def run_outcomes_on_all_cohorts(cursor, grade_start, year_begin, year_end,
    base_pathname):
    for school_year in range(year_begin, year_end+1):
        cohort_tree = build_empty_tree()
        cohort_tree = get_bucket_counts(cursor, cohort_tree,
            grade_begin = grade_start, year_begin = school_year)
        directory = os.path.join(base_pathname, "Descriptives/cohort_figs")
        filename = "cohort_tree_grade_{grade}_in_{year}.png".format(
            grade=grade_start, year=school_year)
        draw_tree_to_file(cohort_tree, os.path.join(directory, filename))
        write_outcomes_to_database(cursor, cohort_tree)

def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            run_outcomes_on_all_cohorts(cursor, 9, 2006, 2012,
            base_pathname)
            run_outcomes_on_all_cohorts(cursor, 10, 2006, 2006,
            base_pathname)
            run_outcomes_on_all_cohorts(cursor, 11, 2006, 2006,
            base_pathname)
            run_outcomes_on_all_cohorts(cursor, 12, 2006, 2006,
            base_pathname)
        connection.commit()
    print('done!')

if __name__ == "__main__":
    main()
