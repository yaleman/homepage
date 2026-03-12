from pathlib import Path

import click
import questionary
import validators

from .config import DEFAULT_COLOUR, DEFAULT_ICON, ConfigFile, Link


def add_link(config: ConfigFile, filepath: Path) -> None:
    """add a link to the config file"""
    link_name = questionary.text("What is the name of the link?").ask()
    if link_name is None:
        return
    while True:
        link_url = questionary.text("What is the url of the link?").ask()
        if link_url is None:
            return
        if validators.url(link_url):
            break
        if questionary.confirm(
            "That doesn't parse as a valid URL, are you sure?"
        ).ask():
            break

    while True:
        link_icon = questionary.text(
            "What's the icon filename?", default=DEFAULT_ICON
        ).ask()
        if link_icon is None:
            return
        if Path(f"images/{link_icon}").exists():
            break
        if questionary.confirm(
            f"The icon doesn't exist at images/{link_icon}, are you sure?"
        ).ask():
            break
    internal_only = questionary.confirm("Is this link internal only?").ask()
    if internal_only is None:
        return
    link_colour = questionary.text("Select a background?", default=DEFAULT_COLOUR).ask()
    if link_colour is None:
        return
    link = Link(
        url=link_url,
        title=link_name,
        icon=link_icon,
        colour=link_colour,
        internal_only=internal_only,
    )
    config.links.append(link)
    print("Adding the following link:")
    print(link.model_dump_json(indent=4))
    if questionary.confirm("Are you sure?").ask():
        config._write_config(filepath)
    else:
        print("Cancelling...")


def remove_link(config: ConfigFile, filepath: Path) -> None:
    """remove a link to the config file"""
    choices = [
        questionary.Choice(title=f"{link.title} - {link.url}", value=index)
        for (index, link) in enumerate(config.links)
    ]
    link_to_remove = questionary.select("Which link to remove?", choices=choices).ask()
    if link_to_remove is None:
        return
    link = config.links[link_to_remove]
    print(f"Removing the following link: {link.model_dump_json(indent=4)}")
    if not questionary.confirm("Are you sure?").ask():
        print("Cancelling...")
        return

    del config.links[link_to_remove]
    config._write_config(filepath)


def edit_link(config: ConfigFile, filepath: Path) -> None:
    """edit a link in the config file"""
    choices = [
        questionary.Choice(title=f"{link.title} - {link.url}", value=index)
        for (index, link) in enumerate(config.links)
    ]
    link_to_edit = questionary.select("Which link to edit?", choices=choices).ask()
    if link_to_edit is None:
        return

    current_link = config.links[link_to_edit]
    link_name = questionary.text(
        "What is the name of the link?", default=current_link.title
    ).ask()
    if link_name is None:
        return

    while True:
        link_url = questionary.text(
            "What is the url of the link?", default=current_link.url
        ).ask()
        if link_url is None:
            return
        if validators.url(link_url):
            break
        if questionary.confirm(
            "That doesn't parse as a valid URL, are you sure?"
        ).ask():
            break

    while True:
        link_icon = questionary.text(
            "What's the icon filename?", default=current_link.icon or DEFAULT_ICON
        ).ask()
        if link_icon is None:
            return
        if Path(f"images/{link_icon}").exists():
            break
        if questionary.confirm(
            f"The icon doesn't exist at images/{link_icon}, are you sure?"
        ).ask():
            break

    internal_only = questionary.confirm(
        "Is this link internal only?", default=current_link.internal_only
    ).ask()
    if internal_only is None:
        return

    link_colour = questionary.text(
        "Select a background?", default=current_link.colour or DEFAULT_COLOUR
    ).ask()
    if link_colour is None:
        return

    updated_link = Link(
        url=link_url,
        title=link_name,
        icon=link_icon,
        colour=link_colour,
        internal_only=internal_only,
    )
    print("Updating the following link:")
    print(updated_link.model_dump_json(indent=4))
    if not questionary.confirm("Are you sure?").ask():
        print("Cancelling...")
        return

    config.links[link_to_edit] = updated_link
    config._write_config(filepath)


@click.command()
@click.option("-f", "--filename", type=click.Path(exists=True), default="links.json")
def cli(filename: str = "links.json") -> None:
    """CLI for homepage"""
    filepath = Path(filename)
    config = ConfigFile.load_config(filepath)
    if config is None:
        print("Failed to load config, bailing...")
        return

    while True:
        try:
            menu_selected = questionary.select(
                "What do you want to do?",
                choices=["Add a link", "Remove a link", "Edit a link", "Exit"],
            ).ask()
            if menu_selected is None:
                return
        except Exception:
            return

        match menu_selected:
            case "Add a link":
                add_link(config, filepath)
            case "Remove a link":
                remove_link(config, filepath)
            case "Edit a link":
                edit_link(config, filepath)
            case "Exit":
                print("Exiting...")
                return


if __name__ == "__main__":
    cli()
