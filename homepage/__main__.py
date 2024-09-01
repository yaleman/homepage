"""CLI interface for homepage"""

import click
import requests
from loguru import logger
from uvicorn import run

from homepage.config import ConfigFile


@click.command()
@click.option(
    "--healthcheck",
    is_flag=True,
    help="Checks if the server healthcheck endpoint is working",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Reload the server on code changes, mainly for testing",
)
@click.option("--port", type=int, default=8000)
@click.option("--host", type=str, default="0.0.0.0")
@click.option(
    "--proxy-headers",
    is_flag=True,
    help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info.",
)
@click.option("--show-config", is_flag=True)
def cli(
    healthcheck: bool = False,
    reload: bool = False,
    port: int = 8000,
    host: str = "0.0.0.0",
    proxy_headers: bool = False,
    show_config: bool = False,
) -> None:
    """homepage server"""
    if show_config:
        config = ConfigFile.load_config()
        print(config.model_dump_json())
    elif healthcheck:
        if host == "0.0.0.0":
            host = "localhost"
        url = f"http://{host}:{port}/health"
        try:
            res = requests.get(url, timeout=5)
            res.raise_for_status()
        except Exception as error:
            logger.error("Healthcheck to {} failed: {}", url, error)
            exit(1)
        logger.success("Healthcheck on {} OK", url)
        exit(0)

    else:
        run(
            app="homepage:get_app",
            factory=True,
            reload=reload,
            host=host,
            port=port,
            proxy_headers=proxy_headers,
        )


if __name__ == "__main__":
    cli()
