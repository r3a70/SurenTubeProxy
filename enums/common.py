from enum import Enum


class Const(Enum):

    HTTPBIN: str = "https://httpbin.org/ip"
    X_RAY_LATEST_RELEASE_DIRECT_DOWNLOAD_URL: str = """
    https://github.com/XTLS/Xray-core/releases/download/v1.8.9/Xray-linux-64.zip
    """.strip()
    TO_JSON_SCRIPT: str = "https://github.com/ImanSeyed/v2ray-uri2json.git"
    VMESS: str = """
    https://raw.githubusercontent.com/Kwinshadow/TelegramV2rayCollector/main/sublinks/vmess.txt
    """.strip()
    VLESS: str = """
    https://raw.githubusercontent.com/Kwinshadow/TelegramV2rayCollector/main/sublinks/vless.txt
    """.strip()
