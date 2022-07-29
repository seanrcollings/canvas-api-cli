import typing as t
from urllib import parse

import requests
from result import Result, Ok, Err


class CanvasApi(requests.Session):
    def __init__(self, domain: str, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_url = f"https://{domain}/api/v1/"
        self.token = token

    def request(self, method, url, *args, **kwargs):
        url = url if url.startswith("http") else parse.urljoin(self.prefix_url, url)
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        kwargs["headers"] = headers
        return super().request(method, url, *args, **kwargs)


def get_canvas_api(
    config: dict[str, t.Any], nickname: str | None = None
) -> Result[CanvasApi, str]:
    instances = config.get("instance", {})

    if nickname:
        name = nickname
    else:
        if "default" in instances:
            name = instances["default"]
        else:
            return Err(
                "No default instance configured,"
                " add a default in the config, or specify an instance explicilty"
            )

    if name in instances:
        instance = instances[name]
    else:
        return Err(f"No instance with name: {name}")

    return Ok(CanvasApi(domain=instance["domain"], token=instance["token"]))
