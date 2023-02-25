""" homepage thing """

from pathlib import Path
import sys
from typing import Union
from jinja2 import Environment, PackageLoader, select_autoescape


from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from .config import ConfigFile

# Checking the setup stuff
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

# init the app
app = FastAPI()

# Jinja things
env = Environment(loader=PackageLoader("homepage"), autoescape=select_autoescape())


@app.on_event("startup")
async def startup() -> None:
    """ Startup things """

    # set up the prometheus exporter on /metrics
    Instrumentator().instrument(app).expose(app)

@app.get("/images/default.png", response_model=None)
async def default_image() -> Union[FileResponse,Response]:
    """default image"""
    if DEFAULT_IMAGE_PATH.exists():
        return FileResponse(DEFAULT_IMAGE_PATH)
    return Response(status_code=404)

@app.get("/apple-touch-icon.png", response_model=None)
async def apple_touch_icon() -> FileResponse:
    """Provides the apple touch icon"""
    return FileResponse(STATIC_DIR / "apple-touch-icon.png")

@app.get("/config")
def get_config() -> ConfigFile:
    """ returns the config file """
    return load_config()

@app.get("/health", response_model=None)
async def healthcheck() -> str:
    """default image"""
    return "OK"

def load_config() -> ConfigFile:
    """ loads the config """
    config_file = Path("links.json")
    if config_file.exists():
        config = ConfigFile.parse_file(config_file.expanduser().resolve())
    else:
        config = ConfigFile(title="This is a site without a config", links=[])
    return config

@app.get("/", response_model=None)
async def homepage() -> Response:
    """home page"""
    template = env.get_template("index.html")
    return Response(template.render(config=load_config()))

app.mount(
    "/static", StaticFiles(directory=STATIC_DIR.expanduser().resolve()), name="static"
)
app.mount(
    "/images", StaticFiles(directory=IMAGES_DIR.expanduser().resolve()), name="images"
)
