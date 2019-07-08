import subprocess

def copy_file(original_file,copy_file):
    with open(original_file, 'r') as ofile:
        with open(copy_file, 'w') as cfile:
            for line in ofile:
                cfile.write(line)
            