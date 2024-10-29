import os
import random
from signal import SIGTERM
import subprocess
import logging
import time
import json
import sqlite3


from database.sqllite import con
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


def run_xray(last_used_proxy: str, max_depth: int = 0) -> tuple[int, str]:

    if max_depth > 100:

        return 0, ""

    if not os.path.exists("/tmp/x-ray-lates/okconfigs"):

        logging.info("okconfigs directory is not found, depth is {}".format(max_depth))
        time.sleep(60)
        return run_xray(last_used_proxy, max_depth + 1)

    configs: list = os.listdir("/tmp/x-ray-lates/okconfigs")
    if not configs:
        logging.info("okconfigs directory is empty {}".format(max_depth))
        time.sleep(60)
        return run_xray(last_used_proxy, max_depth + 1)

    count = 0
    while True:
        if not configs:
            return 0, "not found any Configs in directory"

        configs: list = os.listdir("/tmp/x-ray-lates/okconfigs")
        config: str = random.choice(configs)
        if config != last_used_proxy or count >= 10:
            break

        count += 1

    make_change(config=config)

    process: subprocess.Popen = subprocess.Popen(
        ["./xray", "run", "-c", os.path.join("/tmp/x-ray-lates/okconfigs", config)],
        cwd="/tmp/x-ray-lates/"
    )

    return process.pid, config


def main() -> None:

    cur = con.cursor()
    query: sqlite3.Cursor = cur.execute("SELECT * FROM xray WHERE is_pid = ?;", (1,))
    res = query.fetchone()

    if res:
        cur.execute("DELETE FROM xray WHERE id = ?;", (res[0],))
        db_pid: int = res[2]
        try:
            os.kill(db_pid, SIGTERM)
        except ProcessLookupError as error:
            logging.error(error)
        time.sleep(5)

    pid, proxy = run_xray(last_used_proxy=res[-1] if res else "")
    if not pid:
        logging.error(proxy)
        return 0

    cur.execute(
        "INSERT INTO xray (is_pid, pid, created_at, last_used_proxy) VALUES(?, ?, ?, ?);",
        (1, pid, utcnow(), proxy)
    )
    con.commit()

    cur.close()
