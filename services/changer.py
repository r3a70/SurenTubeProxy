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

    with open(os.path.join("/tmp/x-ray-lates/okconfigs", config)) as file:

        data = json.loads(file.read())

        for port in data.get("inbounds"):

            if port['protocol'] == "socks":

                port.update({"port": 2080})

            else:

                port.update({"port": 2081})

        with open(os.path.join("/tmp/x-ray-lates/okconfigs", config), "w") as new_json_file:
            
            json.dump(data, new_json_file)


def run_xray(last_used_proxy: str) -> int:

    configs: list = os.listdir("/tmp/x-ray-lates/okconfigs")

    while True:

        config: str = random.choice(configs)
        if config != last_used_proxy:
            break

    make_change(config=config)
    
    process: subprocess.Popen = subprocess.Popen(
        ["./xray", "run", "-c", os.path.join("/tmp/x-ray-lates/okconfigs", config)],
        cwd="/tmp/x-ray-lates/",
        # stdout=subprocess.PIPE
    )

    return process.pid, config


def main() -> None:

    res: dict | None = mongo_db[Collections.XRAY.value].find_one({"is_pid": True})
    if res:
        db_pid: int = res.get("pid")
        mongo_db[Collections.XRAY.value].delete_one({"_id": res.get("_id")})
        try:
            os.kill(db_pid, SIGTERM)
        except ProcessLookupError as error:
            logging.error(error)
        time.sleep(5)

    res: dict | None = mongo_db[Collections.XRAY.value].find_one({"is_pid": True})
    if not res:
        pid, proxy = run_xray(last_used_proxy=res.get("last_used_proxy") if res else "")

        mongo_db[Collections.XRAY.value].insert_one(
            {
                "is_pid": True, "pid": pid, "created_at": utcnow(), "last_used_proxy": proxy
            }
        )
