import os

def get_mysql_table_names(mysql_dump_folder):

    mysql_table_names = list()
    table_names_file = os.path.join(mysql_dump_folder, 'ORDER')
    with open(table_names_file, 'r') as file:
        for table_name in file:
            if "commit" not in table_name:
                mysql_table_names.append(table_name.rstrip('\n'))
    return mysql_table_names