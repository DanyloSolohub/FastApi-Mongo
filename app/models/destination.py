from enum import Enum

from beanie import Document, Indexed
from pydantic import HttpUrl


class TransportType(str, Enum):
    HTTP_POST = 'http.post'
    HTTP_GET = 'http.get'
    HTTP_PUT = 'http.put'
    LOG_INFO = 'log.info'
    LOG_WARN = 'log.warn'


class Destination(Document):
    destination_name: Indexed(str, unique=True)
    transport: TransportType
    url: HttpUrl | None = None

    class Settings:
        name = 'destinations'
