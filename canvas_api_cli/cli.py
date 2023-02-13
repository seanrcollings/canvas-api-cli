import json
from pathlib import Path
import typing as t
from typing import Literal
import webbrowser
from result import Err, Ok, UnwrapError
import toml
import xdg
import arc
import requests
import rich
from urllib import parse

from . import option, utils
from .api import get_canvas_api


HTTPMethod = Literal[
    "GET", "POST", "PUT", "DELETE", "HEAD", "CONNECT", "OPTIONS", "TRACE", "PATCH"
]


CONFIG_PATH = xdg.xdg_config_home() / "canvas.toml"

arc.configure(version="0.2.0")

@arc.error_handler(UnwrapError, inherit=True)
def handle_unwrap(e: UnwrapError, ctx: arc.Context):
    arc.print(f"{e}: {e.result.err()}")
    arc.exit(1)

class JSON(dict):
    @classmethod
    def __convert__(cls, value: str):
        if value.startswith("@"):
            path = Path(value.lstrip("@"))
            if path.exists() and path.is_file():
                with path.open("r") as f:
                    value = f.read()
            else:
                raise arc.ConversionError(path, "file does not exist")

        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise arc.ConversionError(
                value, f"failed parsing JSON body: {str(e).split(':')[0]}"
            )


@arc.group
class QueryParams:
    endpoint: str = arc.Argument(desc="The Canvas Endpoint to hit")

    query: list[str] = arc.Option(
        short="q",
        desc="Append to the query string",
        default=[],  # This default collection type isn't working for some reason
    )
    instance: str = arc.Option(
        short="i", desc="What Canvas instance to interact with", default=None
    )

    config: Path = arc.Option(
        short="c",
        desc=f"Path to configuration file to use. Defaults to {CONFIG_PATH}",
        envvar="CANVAS_API_CONFIG",
        default=CONFIG_PATH,
    )

    raw: bool = arc.Flag(
        short="r",
        desc="Don't perform any formatting on the body content. Useful if you want to pipe the data somewhere",
    )
    pagination: bool = arc.Flag(
        short="p", desc="Display pagination information, if it exists"
    )

    data: JSON = arc.Option(
        short="d",
        default=None,
        desc=(
            "Provide body data for POST or PUT requests. "
            "Expected to either be a valid JSON string, or a filename prepended with an @ sign"
        ),
    )

@handle_unwrap
@arc.command("canvas")
def cli():
    ...


@cli.subcommand(("query", "q"))
def query(
    params: QueryParams,
    method: HTTPMethod = arc.Option(short="M", default="GET"),
):
    """Query a Canvas API endpoint

    # Arguments
    method: HTTP method to use
    """
    config = utils.get_config(params.config).expect("Config file missing")
    api = get_canvas_api(config, params.instance).expect("Invalid configuration")

    params.query = params.query or []
    query_params = utils.get_query_params(params.query).expect(
        "Failed to parse query param"
    )
    endpoint = params.endpoint.lstrip("/")

    res = api.request(method, endpoint, json=params.data, params=query_params)

    utils.disply_res(res, params.raw)

    if not res.ok:
        arc.exit(1)

    if params.pagination:
        option.Some(
            "Link"
        ) | res.headers.get | utils.parse_link_header | utils.display_pagination


@cli.subcommand(("get", "g"))
def get(params: QueryParams, ctx: arc.Context):
    """Perform a GET request to the Canvas API

    shorthand for: canvas query <endpoint> -M GET
    """
    ctx.execute(query, params=params, method="GET")


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


@cli.subcommand()
def docs(page: str = "index"):
    """Open Canvas API docs in your browser

    # Arguments
    page: The page you want to open. Defaults to 'index'
    """

    webbrowser.open(f"https://canvas.instructure.com/doc/api/{page}.html")
