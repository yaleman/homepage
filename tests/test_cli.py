from pathlib import Path
from typing import Any, Iterable

import pytest

from homepage import cli as cli_module
from homepage.config import ConfigFile, Hosts, Link


class DummyPrompt:
    def __init__(self, value: Any) -> None:
        self.value = value

    def ask(self) -> Any:
        return self.value


def mock_questionary(
    monkeypatch: pytest.MonkeyPatch,
    *,
    text_answers: Iterable[Any] = (),
    confirm_answers: Iterable[Any] = (),
    select_answers: Iterable[Any] = (),
) -> None:
    text_iter = iter(text_answers)
    confirm_iter = iter(confirm_answers)
    select_iter = iter(select_answers)

    def mock_text(*args: Any, **kwargs: Any) -> DummyPrompt:
        del args, kwargs
        return DummyPrompt(next(text_iter))

    def mock_confirm(*args: Any, **kwargs: Any) -> DummyPrompt:
        del args, kwargs
        return DummyPrompt(next(confirm_iter))

    def mock_select(*args: Any, **kwargs: Any) -> DummyPrompt:
        del args, kwargs
        return DummyPrompt(next(select_iter))

    monkeypatch.setattr(cli_module.questionary, "text", mock_text)
    monkeypatch.setattr(cli_module.questionary, "confirm", mock_confirm)
    monkeypatch.setattr(cli_module.questionary, "select", mock_select)


@pytest.fixture
def temp_config_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    for icon_name in ["existing.svg", "edited.svg", "new-icon.svg"]:
        (image_dir / icon_name).write_text("svg", encoding="utf-8")

    config = ConfigFile(
        title="Test Home",
        hosts=Hosts(external=["example.com"], internal=["localhost:8000"]),
        links=[
            Link(
                title="Existing Link",
                url="https://existing.example.com",
                icon="existing.svg",
                colour="white",
                internal_only=False,
            ),
            Link(
                title="Second Link",
                url="https://second.example.com",
                icon="existing.svg",
                colour="light",
                internal_only=True,
            ),
        ],
        image_dir=image_dir,
    )
    config_path = tmp_path / "links.json"
    config_path.write_text(config.model_dump_json(indent=4), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return config_path


def test_add_link_updates_temp_config(
    temp_config_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = ConfigFile.load_config(temp_config_file)
    mock_questionary(
        monkeypatch,
        text_answers=[
            "New Link",
            "https://new.example.com",
            "new-icon.svg",
            "blue",
        ],
        confirm_answers=[True, True],
    )

    cli_module.add_link(config, temp_config_file)

    updated_config = ConfigFile.load_config(temp_config_file)
    assert len(updated_config.links) == 3
    assert updated_config.links[-1] == Link(
        title="New Link",
        url="https://new.example.com",
        icon="new-icon.svg",
        colour="blue",
        internal_only=True,
    )


def test_remove_link_updates_temp_config(
    temp_config_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = ConfigFile.load_config(temp_config_file)
    mock_questionary(monkeypatch, select_answers=[0], confirm_answers=[True])

    cli_module.remove_link(config, temp_config_file)

    updated_config = ConfigFile.load_config(temp_config_file)
    assert [link.title for link in updated_config.links] == ["Second Link"]


def test_edit_link_updates_temp_config(
    temp_config_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = ConfigFile.load_config(temp_config_file)
    mock_questionary(
        monkeypatch,
        select_answers=[0],
        text_answers=[
            "Edited Link",
            "https://edited.example.com",
            "edited.svg",
            "dark",
        ],
        confirm_answers=[True, True],
    )

    cli_module.edit_link(config, temp_config_file)

    updated_config = ConfigFile.load_config(temp_config_file)
    assert updated_config.links[0] == Link(
        title="Edited Link",
        url="https://edited.example.com",
        icon="edited.svg",
        colour="dark",
        internal_only=True,
    )
