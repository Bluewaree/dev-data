import tarfile
import sys

sys.path.append('..')
import constants.constants as const

def extract_file(file_to_extract,destination_path):
    try:
        with tarfile.open(file_to_extract,'r') as tar:
            tar.extractall(path=destination_path)
    except EOFError as error:
        pass