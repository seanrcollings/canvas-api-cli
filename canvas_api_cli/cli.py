import re
import sys
from typing import Literal
import toml
import xdg
import arc
import requests
import rich
from rich.pretty import pprint
from urllib import parse


class CanvasApi(requests.Session):
    def __init__(self, prefix_url: str, token: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.token = token

    def request(self, method, url, *args, **kwargs):
        url = parse.urljoin(self.prefix_url, url)
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        kwargs["headers"] = headers
        return super().request(method, url, *args, **kwargs)


class CanvasState(arc.types.State):
    api: CanvasApi
    config: dict


@arc.decorator()
def init(ctx):
    config = toml.load("canvas.toml")
    ctx.state["config"] = config
    ctx.state["api"] = CanvasApi(
        prefix_url=f"https://{config['domain']}/api/v1/", token=config["token"]
    )
    yield


cli = arc.namespace("canvas")

cli.decorators.add(init)


Methods = Literal["GET", "POST", "PUT", "DELETE", "get", "post", "put", "delete"]


def info(string: str):
    rich.print(string, file=sys.stderr)


@arc.group
class QueryParams:
    endpoint: str = arc.Argument(description="The Canvas Endpoint to hit")
    raw: bool = arc.Flag(
        short="r",
        description="Don't perform any formatting on the body content. Useful if you want to pipe the data somewhere",
    )
    query: list[str] = arc.Option(short="q", description="Append to the query string")


@cli.subcommand(("query", "q"))
def query(
    params: QueryParams,
    state: CanvasState,
    method: Methods = arc.Option(short="M", default="GET"),
):
    """Query a Canvas API endpoint

    # Arguments
    method: HTTP method to use
    """
    query_params = {key: value for key, value in (v.split("=") for v in params.query)}
    res = state.api.request(method, params.endpoint, params=query_params)

    if params.raw:
        print(res.text)
    else:
        rich.print_json(res.text)

    if method.lower() == "get" and res.headers["Link"]:
        regex = re.compile(r"<(.+)>; rel=\"(.+)\"")
        info("Result was paginated")
        for data in res.headers["Link"].split(","):
            if match := regex.match(data):
                url, relation = match.groups()
                url = url[len(state.api.prefix_url) :]
                parsed = parse.urlparse(url)
                query = ""
                for param in parsed.query.split("&"):
                    query += f" -q {param}"
                info(f"[bold]{relation}[/bold]: canvas g {parsed.path}{query}")

    return res


@cli.subcommand(("get", "g"))
def get(params: QueryParams, ctx: arc.Context):
    """Perform a GET request to the Canvas API

    shorthand for: canvas query <endpoint> -M GET
    """
    res = ctx.execute(query, params=params, method="GET")


@cli.subcommand(("post", "p"))
def post(params: QueryParams, ctx: arc.Context):
    """Perform a POST request to the Canvas API

    shorthand for: canvas query <endpoint> -M POST
    """
    ctx.execute(query, params=params, method="POST")


@cli.subcommand(("put", "u"))
def put(params: QueryParams, ctx: arc.Context):
    """Perform a PUT request to the Canvas API

    shorthand for: canvas query <endpoint> -M PUT
    """
    ctx.execute(query, params=params, method="PUT")


@cli.subcommand(("delete", "d"))
def delete(params: QueryParams, ctx: arc.Context):
    """Perform a DELETE request to the Canvas API

    shorthand for: canvas query <endpoint> -M DELETE
    """
    ctx.execute(query, params=params, method="DELETE")
