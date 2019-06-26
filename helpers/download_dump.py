import subprocess

def download_dump(url,destination_path):
    try:
        command = ['curl', url, '--output', destination_path]
        subprocess.check_output(command)
    except subprocess.CalledProcessError as error:
        raise error