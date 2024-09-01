"""homepage thing"""

from functools import lru_cache
from pathlib import Path
import sys
from typing import Dict, Annotated, Any, Optional, Union
from jinja2 import Environment, PackageLoader, select_autoescape


from fastapi import FastAPI, Header
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from .config import ConfigFile, Hosts, safe_serialize


def get_app() -> FastAPI:
    if Path("/static").exists():
        STATIC_DIR = Path("/static").expanduser().resolve()
    elif Path("./homepage/static/").exists():
        STATIC_DIR = Path("./homepage/static/").expanduser().resolve()
    else:
        logger.error(
            "Couldn't find static basedir, looked in /static, {}", "./homepage/static/"
        )
        sys.exit(1)

    app_config = ConfigFile.load_config()

    if (app_config.image_dir / "default.png").exists():
        DEFAULT_IMAGE_PATH = app_config.image_dir / "default.png"
    else:
        DEFAULT_IMAGE_PATH = app_config.static_dir / "default.png"

    # init the app
    app = FastAPI()
    # compression, default is 9
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    Instrumentator().instrument(app).expose(app)

    # Jinja things
    env = Environment(loader=PackageLoader("homepage"), autoescape=select_autoescape())

    @app.get("/images/default.png", response_model=None, include_in_schema=False)
    async def default_image() -> Union[FileResponse, Response]:
        """default image"""
        if DEFAULT_IMAGE_PATH.exists():
            return FileResponse(DEFAULT_IMAGE_PATH)
        return Response(status_code=404)

    @app.get("/favicon.ico", response_model=None, include_in_schema=False)
    async def favicon() -> Union[FileResponse, Response]:
        """default image"""
        return FileResponse(STATIC_DIR / "favicon.ico")

    @app.get("/apple-touch-icon.png", response_model=None, include_in_schema=False)
    async def apple_touch_icon() -> FileResponse:
        """Provides the apple touch icon"""
        return FileResponse(STATIC_DIR / "apple-touch-icon.png")

    @app.get("/manifest.webmanifest", response_model=None)
    async def manifest() -> Response:
        """Provides the apple touch icon"""
        contents = Path(STATIC_DIR / "manifest.webmanifest").read_text(encoding="utf-8")
        return Response(contents, media_type="application/manifest+json")

    @app.get("/config")
    def get_config(host: Annotated[str | None, Header()] = None) -> Dict[str, Any]:
        """Returns the config file, only accessible from internal hosts"""
        if host in app_config.hosts.internal:
            return safe_serialize(app_config)
        raise HTTPException(
            status_code=401, detail="Only accessible from internal hosts"
        )

    @app.get("/health", response_model=None)
    async def healthcheck() -> str:
        """Healthcheck endpoint"""
        return "OK"

    @lru_cache()
    def load_config(filepath: Optional[str] = None) -> ConfigFile:
        """loads the config"""
        if filepath is None:
            filepath = "links.json"
        config_file = Path(filepath)
        if config_file.exists():
            config = ConfigFile.model_validate_json(
                config_file.read_text(encoding="utf-8")
            )
        else:
            config = ConfigFile(
                title="This is a site without a config",
                links=[],
                hosts=Hosts(internal=[], external=[]),
            )
        config.validate_config()
        return config

    @lru_cache()
    def render_template(filename: str, host: Optional[str]) -> str:
        """caching template rendering"""
        template = env.get_template(filename)
        config = load_config()
        return template.render(
            title=config.title,
            favicon=config.favicon,
            open_in_new_tab=config.open_in_new_tab,
            links=config.get_links(host=host),
        )

    @app.get("/", response_model=None)
    async def homepage(host: Annotated[str | None, Header()] = None) -> Response:
        """home page"""
        return Response(render_template("index.html", host))

    @app.get("/schema.json", description="Returns the JSON schema for the config file")
    async def json_schema() -> Dict[str, Any]:
        """Generates a JSON schema document for the config file"""
        return ConfigFile.model_json_schema()

    app.mount(
        "/static",
        StaticFiles(directory=STATIC_DIR.expanduser().resolve()),
        name="static",
    )
    app.mount("/images", StaticFiles(directory=app_config.image_dir), name="images")
    return app
