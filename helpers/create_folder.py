import subprocess
import os

def create_folder(new_folder_path):
    try:
        command = ['mkdir','-p',new_folder_path]
        subprocess.check_output(command) 
    except subprocess.CalledProcessError as error:
        raise error