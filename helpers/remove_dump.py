import subprocess

def remove_dump(file_to_remove,folder_to_remove):
    try:
        delete_file_command = [
            'rm',
            '-f', 
            file_to_remove
        ]
        delete_folder_command = [
            'rm',
            '-r',
            '-f',
            folder_to_remove
        ]
        subprocess.check_output(delete_file_command)
        subprocess.check_output(delete_folder_command)
    except subprocess.CalledProcessError as error:
        raise error