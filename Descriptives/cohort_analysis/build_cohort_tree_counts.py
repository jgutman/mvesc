import igraph
from igraph import *
import cairo
from mvesc_utility_functions import postgres_pgconnection_generator

def get_bucket_counts(cursor, tree, grade_begin, year_begin,
    schema = 'clean', table = 'wrk_tracking_students'):
    cohort_total_query = """select distinct student_lookup from
        {schema}.{table} where "{year_begin}" = '{grade_begin}'
    """.format(schema=schema, table=table, year_begin=year_begin,
        grade_begin=grade_begin)
    cursor.execute(cohort_total_query)
    cohort_total_students = cursor.fetchall()


    return tree

def draw_tree_to_file(tree, filename="test_tree_plot.png"):
    """
    Draws a tree object to file in given filename.
    Visual attributes and mappings of the tree are defined in this function.
    Tree attributes should be fully defined before calling this function.
    """

    tree_layout = tree.layout("tree")
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

    ### putting some basic useful commands here temporarily for reference
    print(tree) # 18 vertices, 17 edges, 4 vertex attributes, 0 edge attributes

    # cohort_vertex = tree.vs.select(description='cohort total')
    # assert(len(cohort_vertex) == 1)
    # cohort_index = [v.index for v in cohort_vertex][0]
    # tree.vs[cohort_index].attributes()
    # assert([v["count"] for v in cohort_vertex][0] == 0)
    # student_list = [1000, 2000, 3000, 4000]
    ### index first, then attribute name! reverse order doesn't change value
    # tree.vs[cohort_index]["students"] = student_list
    # tree.vs[cohort_index]["count"] = len(student_list)
    # assert([v["count"] for v in cohort_vertex][0] == len(student_list))
    # assert([v["students"] for v in cohort_vertex][0] == student_list)
    # tree.vs[cohort_index].attributes()

    return tree

def main():
    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            cohort_tree = build_empty_tree()
            cohort_tree = get_bucket_counts(
                cursor, cohort_tree, grade_begin = '09', year_begin = 2010)
            cursor.execute(query)
        connection.commit()
    print('done!')

if __name__ == "__main__":
    main()
