""" homepage thing """

from pathlib import Path
import sys
from typing import List, Optional, Union
from jinja2 import Environment, PackageLoader, select_autoescape


from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from loguru import logger
from pydantic import BaseSettings, BaseModel, validator


class Link(BaseModel):
    """link object"""

    url: str
    title: str
    icon: Optional[str] = "default.png"
    colour: Optional[str] = "white"


class ConfigFile(BaseSettings):
    """link list"""

    title: str
    favicon: Optional[str] = None
    links: List[Link]

    @validator("favicon")
    def validate_favicon(cls, value: Optional[str]) -> str:
        if value is None:
            return "/static/favicon.svg"
        return f"/images/{value}"



if Path("/images").exists():
    IMAGES_DIR = Path("/images").expanduser().resolve()
elif Path("./images/").exists():
    IMAGES_DIR = Path("./images/").expanduser().resolve()
else:
    logger.error("Couldn't find images basedir, looked in /images, {}", "./images/")
    sys.exit(1)
logger.info("IMAGES_DIR: {}", IMAGES_DIR)

if Path("/static").exists():
    STATIC_DIR = Path("/static").expanduser().resolve()
elif Path("./homepage/static/").exists():
    STATIC_DIR = Path("./homepage/static/").expanduser().resolve()
else:
    logger.error(
        "Couldn't find static basedir, looked in /static, {}", "./homepage/static/"
    )
    sys.exit(1)
logger.info("STATIC_DIR: {}", STATIC_DIR.expanduser().resolve())

if (IMAGES_DIR / "default.png").exists():
    DEFAULT_IMAGE_PATH = IMAGES_DIR / "default.png"
else:
    DEFAULT_IMAGE_PATH = STATIC_DIR / "default.png"

app = FastAPI()


# Jinja things
env = Environment(loader=PackageLoader("homepage"), autoescape=select_autoescape())


@app.get("/images/default.png")
async def default_image() -> Union[FileResponse,Response]:
    """default image"""
    if DEFAULT_IMAGE_PATH.exists():
        return FileResponse(DEFAULT_IMAGE_PATH)
    return Response(status_code=404)


@app.get("/health")
async def healthcheck() -> str:
    """default image"""
    return "OK"

@app.get("/")
async def homepage() -> Response:
    """home page"""
    linkfile = Path("links.json")
    if linkfile.exists():
        config = ConfigFile.parse_file(linkfile.expanduser().resolve())
    else:
        config = ConfigFile(title="This is a site without a config", links=[])
    template = env.get_template("index.html")
    return Response(template.render(config=config))

app.mount(
    "/static", StaticFiles(directory=STATIC_DIR.expanduser().resolve()), name="static"
)
app.mount(
    "/images", StaticFiles(directory=IMAGES_DIR.expanduser().resolve()), name="images"
)
