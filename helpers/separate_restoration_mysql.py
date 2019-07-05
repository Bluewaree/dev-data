from multiprocessing.dummy import Pool as ThreadPool

destination_path = ""

def process(mysql_table):
    print(f'-------------- Processing {mysql_table} ----------------')
    csv_file = os.path.join(destination_path,'dump','{0}.csv'.format(mysql_table))
    mysql.restore_db(csv_file,mysql_table)
    print(f'-------------- Processing ended ----------------')


def separate_restoration(mysql_tables, destination_path):
    global destination_path = destination_path
    pool = ThreadPool(5)
    pool.map(process, mysql_tables)
    pool.close()
    pool.join()
