import os
import random
from signal import SIGTERM
import subprocess
import logging
import time
import json


from enums.collections import Collections
from database.mongodb import mongo_db
from utils.times import utcnow


def make_change(config: str) -> None:

    mode = os.getenv("MODE")
    proxies = {
        "dev_socks": 5080, "dev_http": 5081,
        "prd_socks": 2080, "prd_http": 2081
    }

    with open(os.path.join("/tmp/x-ray-lates/okconfigs", config)) as file:

        data = json.loads(file.read())

        for port in data.get("inbounds"):

            if port['protocol'] == "socks":

                port.update({"port": proxies[f"{mode}_socks"]})

            else:

                port.update({"port": proxies[f"{mode}_http"]})

        with open(os.path.join("/tmp/x-ray-lates/okconfigs", config), "w") as new_json_file:

            json.dump(data, new_json_file)


def run_xray(last_used_proxy: str) -> tuple[int, str]:

    configs: list = os.listdir("/tmp/x-ray-lates/okconfigs")

    while True:
        if not configs:
            return 0, "not found any Configs in directory"

        config: str = random.choice(configs)
        if config != last_used_proxy:
            break

    make_change(config=config)

    process: subprocess.Popen = subprocess.Popen(
        ["./xray", "run", "-c", os.path.join("/tmp/x-ray-lates/okconfigs", config)],
        cwd="/tmp/x-ray-lates/"
    )

    return process.pid, config


def main() -> None:

    logging.warning("main() in changer.py")

    res: dict | None = mongo_db[Collections.XRAY.value].find_one_and_delete({"is_pid": True})
    if res:
        db_pid: int = res.get("pid")
        try:
            os.kill(db_pid, SIGTERM)
        except ProcessLookupError as error:
            logging.error(error)
        time.sleep(5)

    pid, proxy = run_xray(last_used_proxy=res.get("last_used_proxy") if res else "")
    if not pid:
        logging.error(proxy)
        return 0

    mongo_db[Collections.XRAY.value].insert_one(
        {
            "is_pid": True, "pid": pid, "created_at": utcnow(), "last_used_proxy": proxy
        }
    )
