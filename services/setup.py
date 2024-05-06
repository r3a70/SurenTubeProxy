from zipfile import ZipFile
import os
import subprocess
import time
import logging
import requests


from enums.common import Const


def download_requirements() -> None:

    if os.path.exists("/tmp/x-ray-lates.zip"):

        return

    url: str = Const.X_RAY_LATEST_RELEASE_DIRECT_DOWNLOAD_URL.value

    with requests.Session().get(url=url) as response:

        with open(file="/tmp/x-ray-lates.zip", mode="wb") as file:

            file.write(response.content)


def extract_zip() -> None:

    if os.path.exists("/tmp/x-ray-lates"):

        return

    with ZipFile("/tmp/x-ray-lates.zip") as zip:

        zip.extractall("/tmp/x-ray-lates")

    subprocess.run(["chmod", "+x", "xray"], cwd="/tmp/x-ray-lates/")


def download_config_2_json() -> None:

    if os.path.exists("/tmp/x-ray-lates/v2ray-uri2json"):

        return

    subprocess.run(["git", "clone", Const.TO_JSON_SCRIPT.value], cwd="/tmp/x-ray-lates/")


def get_configs() -> None:

    try:

        with requests.Session().get(url=Const.VMESS.value) as response:

            with open("/tmp/x-ray-lates/v2ray-uri2json/vmess.txt", "wb") as file:

                file.write(response.content)

        with requests.Session().get(url=Const.VLESS.value) as response:

            with open("/tmp/x-ray-lates/v2ray-uri2json/vless.txt", "wb") as file:

                file.write(response.content)

    except Exception as error:

        logging.error(error)


def convert_and_move_configs() -> None:

    if not os.path.exists("/tmp/x-ray-lates/configs"):

        os.mkdir("/tmp/x-ray-lates/configs")

    else:

        for file in os.listdir("/tmp/x-ray-lates/configs"):

            os.remove(os.path.join("/tmp/x-ray-lates/configs", file))

    all_configs = 0
    with open("/tmp/x-ray-lates/v2ray-uri2json/vmess.txt") as content:

        for index, line in enumerate(content.readlines(), start=1):

            val = index
            if val < 10:
                val = f"0{index}"

            vmess: str = line.strip()
            if vmess:
                command: list = [
                    "bash",
                    "scripts/vmess2json.sh",
                    "--http-proxy", "4081",
                    "--socks5-proxy", "4080",
                    vmess
                ]
                subprocess.run(
                    command,
                    capture_output=True,
                    cwd="/tmp/x-ray-lates/v2ray-uri2json",
                )
                subprocess.run(
                    ["mv", "config.json", f"../configs/{val}_config_vmess.json"],
                    capture_output=True,
                    cwd="/tmp/x-ray-lates/v2ray-uri2json",
                )
                all_configs += 1

    with open("/tmp/x-ray-lates/v2ray-uri2json/vless.txt") as content:

        for index, line in enumerate(content.readlines(), start=all_configs + 1):

            val = index
            if val < 10:
                val = f"0{index}"

            vless: str = line.strip()
            if vless:
                command: list = [
                    "bash",
                    "scripts/vless2json.sh",
                    "--http-proxy", "4081",
                    "--socks5-proxy", "4080",
                    vless
                ]
                subprocess.run(
                    command,
                    capture_output=True,
                    cwd="/tmp/x-ray-lates/v2ray-uri2json",
                )
                subprocess.run(
                    ["mv", "config.json", f"../configs/{val}_config_vless.json"],
                    capture_output=True,
                    cwd="/tmp/x-ray-lates/v2ray-uri2json",
                )


def test_configs() -> None:

    for config in os.listdir("/tmp/x-ray-lates/configs"):

        code = subprocess.run(
            [
                "./xray", "run", "-c",
                os.path.join("/tmp/x-ray-lates/configs", config),
                "-test"
            ],
            cwd="/tmp/x-ray-lates",
            capture_output=True
        )
        if code.returncode != 0:

            os.remove(os.path.join("/tmp/x-ray-lates/configs", config))


def test_configs_connection() -> None:

    if not os.path.exists("/tmp/x-ray-lates/okconfigs"):

        os.mkdir("/tmp/x-ray-lates/okconfigs")

    for file in os.listdir("/tmp/x-ray-lates/okconfigs"):

        os.remove(os.path.join("/tmp/x-ray-lates/okconfigs", file))

    configs: list = os.listdir("/tmp/x-ray-lates/configs")

    for config in configs:

        process: subprocess.Popen = subprocess.Popen(
            ["./xray", "run", "-c", os.path.join("/tmp/x-ray-lates/configs", config)],
            cwd="/tmp/x-ray-lates/"
        )

        time.sleep(10)
        try:
            mode = os.getenv("MODE")
            port = {
                "dev_socks": 4080, "dev_http": 4081,
                "prd_socks": 2080, "prd_http": 2081
            }
            proxies: dict = {
                "http": f"http://localhost:{port[f'{mode}_http']}",
                "https": f"http://localhost:{port[f'{mode}_http']}"
            }
            with requests.Session() as session:

                response = session.get(url=Const.HTTPBIN.value, proxies=proxies, timeout=5)
                data: dict = response.json()

                if data.get("origin"):

                    logging.info(
                        "test-configs-connection: This {} works. his result is {}".format(
                            config, data
                        )
                    )
                    process.kill()
                    os.rename(
                        src=os.path.join("/tmp/x-ray-lates/configs", config),
                        dst=os.path.join("/tmp/x-ray-lates/okconfigs",
                                         f"{data.get('origin')}.json"),
                    )

        except Exception as error:
            process.kill()
            logging.error("test-configs-connection: An error acurred %s\n", error)
            os.remove(os.path.join("/tmp/x-ray-lates/configs", config))


def main() -> None:

    download_requirements()
    extract_zip()
    download_config_2_json()
    get_configs()
    convert_and_move_configs()
    test_configs()
    test_configs_connection()
