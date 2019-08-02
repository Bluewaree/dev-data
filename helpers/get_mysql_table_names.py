import os

def get_mysql_table_names(mysql_dump_folder):
    mysql_table_names = list()
    for filename in os.listdir(mysql_dump_folder):
        if "users" in filename:
            mysql_table_names.append(filename.replace('.csv',''))  
    mysql_table_names.sort(key=lambda filename: os.path.getsize(os.path.join(mysql_dump_folder,f"{filename}.csv")))
    return mysql_table_names