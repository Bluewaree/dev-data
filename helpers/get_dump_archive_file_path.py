import os

def get_dump_archive_file_path(archives_base_folder,database_type,dump_date):
    return os.path.join(archives_base_folder,f'{database_type}-dump-{dump_date}.tar.gz')   