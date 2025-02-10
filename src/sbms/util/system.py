import platform

def get_os():
    os_type = platform.system()
    if os_type == "Linux":
        return "Linux"
    elif os_type == "Windows":
        return "Windows"
    elif os_type == "Darwin":
        return "MacOS"
    else:
        return "Unknown"
