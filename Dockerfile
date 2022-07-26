FROM python:3.10-slim
# FROM python:3.10-alpine

########################################
# add a user so we're not running as root
########################################
# ubuntu mode
RUN useradd homepage

RUN mkdir -p /home/homepage/
RUN chown homepage /home/homepage -R

RUN mkdir -p build/homepage

WORKDIR /build

COPY homepage homepage
COPY poetry.lock .
COPY pyproject.toml .

RUN chown homepage /build -R
WORKDIR /
USER homepage

RUN python -m pip install --upgrade --no-warn-script-location pip
RUN python -m pip install --no-cache --no-warn-script-location /build
USER root
RUN rm -rf /build
USER homepage
COPY ./homepage/static /homepage/static
RUN python -m pip uninstall poetry
RUN rm -rf /home/homepage/.cache/

# to allow xff headers from docker IPs
ENV FORWARDED_ALLOW_IPS="*"
EXPOSE 8000

CMD /home/homepage/.local/bin/uvicorn homepage:app --host 0.0.0.0 --port 8000
