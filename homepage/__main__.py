"""CLI interface for homepage"""

import click
from uvicorn import run

from homepage.config import ConfigFile


@click.command()
@click.option("--reload", is_flag=True)
@click.option("--port", type=int, default=8000)
@click.option("--host", type=str, default="0.0.0.0")
@click.option("--proxy-headers", is_flag=True)
@click.option("--show-config", is_flag=True)
def cli(
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
