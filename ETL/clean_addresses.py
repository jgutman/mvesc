import yaml
import re
import os, sys

pathname = os.path.dirname(sys.argv[0])
full_pathname = os.path.abspath(pathname)
split_pathname = full_pathname.split(sep="mvesc")
base_pathname = os.path.join(split_pathname[0], "mvesc")
parentdir = os.path.join(base_pathname, "ETL")
sys.path.insert(0,parentdir)

sys.path.insert(0, os.path.join(base_pathname, 'Models_Results'))
from my_timer import Timer

from mvesc_utility_functions import *

def parse_addresses(addresses, shortened):
    addresses = [address.title() if address else None
        for address in addresses]
    addresses = [re.sub('[.,]', '', address) if address else None
        for address in addresses]
    addresses = [re.sub(r'\s+', ' ', address) if address else None
        for address in addresses]
    pattern = re.compile('|'.join(shortened.keys()))
    addresses = [pattern.sub(lambda x: shortened[x.group()], address)
        if address else None
        for address in addresses]
    return addresses

def main(argv):
    
    clean_schema = argv[0]

    with open(os.path.join(base_pathname,
        'ETL/clean_addresses.yaml'), 'r') as f:
        shortened = yaml.load(f)

    with postgres_pgconnection_generator() as connection:
        with connection.cursor() as cursor:
            query_start_over = """drop table if exists all_snapshots;
                drop table if exists snapshots_updated;
                create temp table all_snapshots as
                select * from {s}.all_snapshots;
            """.format(s=clean_schema)
            query_create_street_index = """create index old_streets on
                all_snapshots (street)"""
            cursor.execute(query_start_over)
            cursor.execute(query_create_street_index)

            query_get_addresses = """select street from all_snapshots"""
            cursor.execute(query_get_addresses)
            addresses = [i[0] for i in cursor.fetchall()]

            with Timer('parse_address') as t:
                standardized_addresses = parse_addresses(addresses, shortened)
                assert(len(standardized_addresses)==len(addresses))
                assert([i for i,j in enumerate(addresses) if not j] ==
                    [i for i,j in enumerate(standardized_addresses) if not j])

            map_addresses = {k: v for k, v in
                    zip(addresses, standardized_addresses) if k!=v}
            rows = [{'old_address': k, 'new_address': v} for k, v in
                    map_addresses.items()]

            with Timer('replace_address') as t:
                cursor.execute("""alter table all_snapshots
                    add column street_clean_bare varchar(80)""")
                cursor.executemany("""update all_snapshots
                    set street_clean_bare=%(new_address)s
                    where street=%(old_address)s
                """, rows)
                cursor.execute("""drop table {s}.all_snapshots;
                    create table {s}.all_snapshots as
                    select *, coalesce(street_clean_bare, street) street_clean
                        from all_snapshots;
                    alter table {s}.all_snapshots
                    drop column street_clean_bare;"""\
                               .format(s=clean_schema))
            connection.commit()

if __name__ == '__main__':
    main()
