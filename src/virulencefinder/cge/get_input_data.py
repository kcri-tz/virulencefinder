import hashlib
import sys

from .config import Config

def get_call_parameters(conf: Config) -> dict:
    parameters = vars(conf).copy()
    return parameters


def get_software_exec_res(conf: Config) -> dict:
    software_exec_res = {
        "type": "software_exec",
        "command": " ".join(sys.argv),
        "parameters": get_call_parameters(conf)
    }
    software_exec_res["key"] = hashlib.sha1(
        bytes(software_exec_res["command"], 'UTF-8')).hexdigest()
    return software_exec_res
