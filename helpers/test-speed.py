import speedtest

def get_download_speed():
    s = speedtest.Speedtest()
    s.download()
    results_dict = s.results.dict()
    return results_dict['download']/1024/1024/8
