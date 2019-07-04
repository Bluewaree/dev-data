import os

def get_mysql_table_names(mysql_dump_folder):

    mysql_table_names = list()
    for (dirpath, dirnames, filenames) in os.walk(mysql_dump_folder):
        mysql_table_names += [file.replace(".csv","") for file in filenames if file.endswith(".csv")]
    return mysql_table_names