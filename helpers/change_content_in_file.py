import subprocess

def change_content_in_file(content_to_change,new_content,file_to_change):
    try:
        command = ['sed',
            '-i.bak',
            f"s/{content_to_change}/{new_content}/g",
            file_to_change
        ]
        subprocess.check_output(command) 
    except subprocess.CalledProcessError as error:
        raise error