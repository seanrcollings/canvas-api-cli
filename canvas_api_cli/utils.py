import typing as t
from pathlib import Path
import re
import sys
from urllib import parse
import arc
import requests
from result import Err, Ok, Result
import toml

import rich

link_regex = re.compile(r"<(.+)>; rel=\"(.+)\"")


def parse_link_header(header: str):
    parsed: dict[str, str] = {}

    for data in header.split(","):
        if match := link_regex.match(data):
            url, relation = match.groups()
            parsed[relation] = parse.unquote(url)

    return parsed


def info(string: str):
    rich.print(string, file=sys.stderr)


def get_config(path: Path) -> Result[dict[str, t.Any], str]:
    if not path.exists():
        return Err(f"{path} does not exist")
    if not path.is_file():
        return Err(f"{path} is not a file")

    config = toml.load(path)

    return Ok(config)


def disply_res(res: requests.Response, raw: bool = False):
    if res.ok:
        if raw:
            arc.print(res.text)
        else:
            rich.print_json(res.text)
    else:
        info(f"[red]Request Failed[/red]: {res.status_code}")
        if res.headers.get("Content-Type", "").startswith("application/json"):
            rich.print_json(res.text)


def display_pagination(links: dict[str, str]):
    info("Result was paginated")
    for relation, url in links.items():
        parsed = parse.urlparse(url)
        endpoint = parsed.path[len("/api/v1/") :]
        query = " ".join(f"-q {p}" for p in parsed.query.split("&"))

        info(
            f"[bold]{relation}[/bold]: canvas g "
            f"[magenta]{endpoint}[/magenta] {query}"
        )


def get_query_params(lst: list[str]) -> Result[list[tuple[str, str]], str]:
    res: list[tuple[str, str]] = []

    for query in lst:
        if "=" not in query:
            return Err(f"Invalid query param: {query}")

        name, value = query.split("=")

        res.append((name, value))

    return Ok(res)