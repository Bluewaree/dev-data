
def format_string(string):
    if string is not None:  
        string = string.replace('\\',"\\\\")      
        string = string.replace('"','\\"')
        string = f"\"{string}\""
    else:
        string = "Null"
    return string