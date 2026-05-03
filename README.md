# homepage

Home Page for clicky link things.

## Installation

Install this library using `pip`:

```shell
python -m pip install git+https://github.com/yaleman/homepage
```

## Usage

Spin up the docker container, mount `links.json` in the working dir - `/links.json`

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:

```shell
cd homepage
python -m pip install uv
uv sync
```

To run it natively:

```shell
$ mise start 
# or
$ uv run uvicorn --factory homepage:get_app --port 8000 --host 0.0.0.0 --reload
```

Or in docker:

```shell
mise run_container
```

## Thanks

- Home Icon from [Marek Polakovic @ The Noun Project](https://thenounproject.com/icon/home-113939/)
- [FastAPI](https://fastapi.tiangolo.com/) for making this so very easy.
