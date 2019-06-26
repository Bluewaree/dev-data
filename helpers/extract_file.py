import tarfile
import os
import sys

sys.path.append('..')
import constants.constants as const

def extract_file(file_to_extract,destination_path):
    try:
        with tarfile.open(file_to_extract,'r') as tar:
            members_names = [f'dump/github/{collection}.bson' for collection in const.COLLECTIONS]
            members = [member for member in tar.getmembers() if member.name in members_names]
            tar.extractall(members=members, path=destination_path)
    except EOFError as error:
        pass