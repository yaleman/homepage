""" homepage thing """

from pathlib import Path
import sys
from typing import List, Optional, Union
from jinja2 import Environment, PackageLoader, select_autoescape


from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseSettings, BaseModel

class Link(BaseModel):
    """ link object """
    url: str
    title: str
    icon: Optional[str] = "default.png"
    colour: Optional[str] = "white"

class ConfigFile(BaseSettings):
    """ link list """
    title: str
    favicon: Optional[str] = "default.png"
    links: List[Link]



app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__name__).expanduser().resolve() / "static"), name="static")


env = Environment(
    loader=PackageLoader("homepage"),
    autoescape=select_autoescape()
)

# STATIC_DIR = Path(__name__).expanduser().resolve() / "static"
# print(f"{STATIC_DIR=}")

# @app.get("/static/{filename}")
# async def static_file(filename: str) -> Union[FileResponse, Response]:
#     """ returns a static file"""
#     static_file = STATIC_DIR / filename

#     if not static_file.exists():
#         print(f"Couldn't find {static_file}")
#         return Response(status_code=404)
#     return FileResponse(static_file)

@app.get("/")
async def index() -> Response:
    """ home page """
    linkfile = Path("links.json")
    if linkfile.exists():
        config = ConfigFile.parse_file(linkfile.expanduser().resolve())
    else:
        config = ConfigFile(title="This is a site without a config", links=[])
    template = env.get_template("index.html")

    return Response(template.render(config=config))
