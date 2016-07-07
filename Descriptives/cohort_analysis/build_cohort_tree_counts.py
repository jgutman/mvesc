import igraph
from igraph import *
from mvesc_utility_functions import postgres_pgconnection_generator

def get_bucket_counts(cursor, tree, grade_begin, year_begin):



    return tree

def build_empty_tree():
    """
    Builds an empty tree obj for outcome classification. Vertices are named and
    counts for each vertex are initialized at zero. Pass tree along with cursor
    to get_bucket_counts method to fill in student counts at each vertex.
    """
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

    ### putting some basic useful commands here temporarily for reference
    print(tree)
    # cohort_vertex = tree.vs.select(description='cohort total')
    # assert(len(cohort_vertex) == 1)
    # cohort_index = [v.index for v in cohort_vertex][0]
    # tree.vs[cohort_index].attributes()
    # assert([v['count'] for v in cohort_vertex][0] == 0)
    # student_list = [1000, 2000, 3000, 4000]
    ### index first, then attribute name! reverse order doesn't change value
    # tree.vs[cohort_index]['students'] = student_list
    # tree.vs[cohort_index]['count'] = len(student_list)
    # assert([v['count'] for v in cohort_vertex][0] == len(student_list))
    # assert([v['students'] for v in cohort_vertex][0] == student_list)
    # tree.vs[cohort_index].attributes()
    # tree_layout = tree.layout('rt')


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
