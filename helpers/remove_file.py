import subprocess

def remove_file(file_to_remove):
    try:
        delete_file_command = [
            'rm',
            '-f', 
            file_to_remove
        ]
        subprocess.check_output(delete_file_command)
    except subprocess.CalledProcessError as error:
        raise error