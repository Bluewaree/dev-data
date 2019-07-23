import os

def get_dump_folder_endpoint(archives_base_folder,database_type,dump_date):
    dump_enterence_folder = os.path.join(archives_base_folder,f'{database_type}-dump-{dump_date}')

    for (dirpath, dirnames, filenames) in os.walk(dump_enterence_folder):
        for file in filenames:
            dump_folder_containing_files = dirpath.rsplit(dump_enterence_folder,1)[1]
            break           
         
    dump_folder_path = dump_enterence_folder + dump_folder_containing_files

    return dump_folder_path