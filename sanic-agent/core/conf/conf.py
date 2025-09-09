from datetime import time
from typing import Any, Callable


def t_s():
    return int(time.time() * 1000)


class Conf:
    def __init__(self):
        pass

    @classmethod
    def must_load(cls, path: str, v: dict[Any, Any], *args: Callable[..., Any]) -> None:
        pass


Conf.must_load("/etc/sanic", {}, t_s)

conf1 = Conf



a = {
    
}