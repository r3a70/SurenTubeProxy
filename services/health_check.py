import requests
import logging
import os


from services.changer import main
from enums.collections import Collections
from database.mongodb import mongo_db


HTTPBIN: str = "https://httpbin.org/ip"


def health_check_ips() -> bool:

    try:
        proxies: dict = {"http": "http://localhost:2081", "https": "http://localhost:2081"}
        with requests.Session() as session:

            response = session.get(url=HTTPBIN, proxies=proxies, timeout=10)
            data: dict = response.json()

            if data.get("origin"):

                logging.info("ip works. his result is %s", data)

    except Exception as error:
        logging.error("An error acurred %s\n", error)
        query: dict | None = mongo_db[Collections.XRAY.value].find_one({"is_pid": True})
        ip: str = query.get("last_used_proxy") if query else ""

        if os.path.exists(os.path.join("/tmp/x-ray-lates/okconfigs", ip)):

            os.remove(os.path.join("/tmp/x-ray-lates/okconfigs", ip))
        
        main()
