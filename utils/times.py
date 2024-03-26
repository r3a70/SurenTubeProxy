from datetime import datetime


def now() -> datetime:

    return datetime.now()


def utcnow() -> str:

    return datetime.utcnow()
