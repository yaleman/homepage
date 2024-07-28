"""config object"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic import Field, field_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_ICON = "default.png"
DEFAULT_COLOUR = "white"


class Link(BaseModel):
    """link object"""

    url: str
    title: str
    icon: Optional[str] = DEFAULT_ICON
    colour: Optional[str] = DEFAULT_COLOUR
    internal_only: bool = Field(False)


class Hosts(BaseModel):
    external: List[str] = Field([])
    internal: List[str] = Field(["localhost"])

    @field_validator("internal")
    def validate_internal(cls, value: List[str]) -> List[str]:
        if os.getenv("CI") is not None:
            return ["localhost"]
        return value


def safe_serialize(config: BaseSettings) -> Dict[str, Any]:
    """serialize it without giving away secrets"""
    res = config.model_dump()
    res["hosts"] = Hosts(internal=[], external=[])
    return res


class ConfigFile(BaseSettings):
    """config file things"""

    favicon: Optional[str] = None
    links: List[Link]
    open_in_new_tab: Optional[bool] = False
    title: str
    hosts: Hosts
    image_dir: Path = Field(default="./images")
    static_dir: Path = Field(default=Path(__file__).parent / "static")

    model_config = SettingsConfigDict(env_prefix="HOMEPAGE_")

    @field_validator("favicon")
    @classmethod
    def validate_favicon(cls, value: Optional[str] = None) -> str:
        """validates the favicon setting"""
        if value is None:
            return "/static/favicon.svg"
        elif value.startswith("/"):
            value = value[1:]
        return f"/images/{value}"

    def validate_config(self) -> None:
        """check things are gud"""
        if not self.hosts.external and not self.hosts.internal:
            raise ValueError("You need to specify either an internal or external host!")

    @field_validator("image_dir", mode="after")
    @classmethod
    def validate_image_dir(cls, value: Path) -> Path:
        """validates the image path exists"""
        if not value.exists():
            raise ValueError(f"Image directory '{value}' does not exist!")
        return value

    @field_validator("static_dir", mode="after")
    @classmethod
    def validate_static_dir(cls, value: Path) -> Path:
        """validates the static path exists"""
        if not value.exists():
            raise ValueError(f"Static directory '{value}' does not exist!")
        return value

    @classmethod
    def load_config(cls, filename: Optional[Path] = None) -> "ConfigFile":
        """load a config file from a filepath"""
        if filename is None:
            filename = Path(os.getenv("HOMEPAGE_CONFIG_FILE", "links.json"))
        if not filename.exists():
            raise ValueError(f"Config file '{filename}' does not exist!")

        return ConfigFile.model_validate_json(filename.read_text(encoding="utf-8"))

    def get_links(self, host: Optional[str] = None) -> List[Link]:
        """returns the links, checks if we're allowed to"""
        if self.hosts.internal:
            # we have specified internal hosts
            if host is None:
                include_internal = False
            elif host in self.hosts.internal:
                include_internal = True
            else:
                include_internal = False
        else:
            include_internal = True

        if host is not None and host in self.hosts.external:
            include_internal = False

        logger.debug(f"{include_internal=}")

        res = []
        for link in self.links:
            if link.internal_only and not include_internal:
                continue
            res.append(link)
        return res
