import os
import logging

import requests
from yt_dlp import YoutubeDL

from services.changer import main


HTTPBIN: str = "https://httpbin.org/ip"


def health_check_ips(is_recursive: bool = False) -> bool:

    try:
        mode = os.getenv("MODE")
        port = {
            "dev_socks": 5080, "dev_http": 5081,
            "prd_socks": 2080, "prd_http": 2081
        }

        proxies: dict = {
            "http": f"http://localhost:{port[f'{mode}_http']}",
            "https": f"http://localhost:{port[f'{mode}_http']}"
        }
        ydl_opts = {
            'proxy': proxies["http"],
            'quite': True
        }

        with YoutubeDL(ydl_opts) as ytdlp:

            ytdlp.extract_info(
                url="https://www.youtube.com/watch?v=ido8s_vGqcM",
                download=False
            )

        with requests.Session() as session:

            response = session.get(url=HTTPBIN, proxies=proxies, timeout=10)
            data: dict = response.json()

            if data.get("origin"):

                logging.info("ip works. his result is %s", data)

    except Exception as error:

        logging.error("An error acurred %s\n", error)

        if not is_recursive:

            return health_check_ips(is_recursive=True)

        else:

            main()
