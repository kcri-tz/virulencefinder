import sys
import hashlib


def get_software_exec_res(conf) -> dict:
    software_exec_res = {
        "type": "software_exec",
        "command": " ".join(sys.argv),
        "parameters": get_call_parameters(conf)
    }
    software_exec_res["key"] = hashlib.sha1(
        bytes(software_exec_res["command"], 'UTF-8')).hexdigest()
    return software_exec_res


def get_call_parameters(conf) -> dict:
    parameters = vars(conf).copy()
    # Delete DBConf object as it is not serializable and not relevant
    del parameters["db_conf"]
    return parameters

