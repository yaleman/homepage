""" CLI interface for homepage """

import click
import uvicorn #type: ignore

@click.command()
@click.option("--reload", is_flag=True)
@click.option("--port", type=int, default=8000)
@click.option("--host", type=str, default="0.0.0.0")
@click.option("--proxy-headers", is_flag=True)
def cli(
    reload: bool=False,
    port: int=8000,
    host: str="0.0.0.0",
    proxy_headers: bool=False,
    ) -> None:
    """ homepage server """
    uvicorn.run(
        app="homepage:app",
        reload=reload,
        host=host,
        port=port,
        proxy_headers=proxy_headers,
        )

if __name__ == "__main__":
    cli()
