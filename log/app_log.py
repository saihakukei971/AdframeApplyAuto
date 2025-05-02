from logging import getLogger, config
import json
import datetime
import os

if not os.path.exists("./log/adframelog"):
    os.mkdir("./log/adframelog")

logFolderPath = f"./log/adframelog/{datetime.datetime.now().strftime('%Y%m%d')}"
if not os.path.exists(logFolderPath):
    os.mkdir(logFolderPath)

with open("./log/log_config.json", "r") as f:
    log_config = json.load(f)

log_config["handlers"]["fileHandler"]["filename"] = f"{logFolderPath}/process.log"
config.dictConfig(log_config)

def get_my_logger(name: str):
    logger = getLogger(name)

    return logger

if __name__ == "__main__":
    get_my_logger()